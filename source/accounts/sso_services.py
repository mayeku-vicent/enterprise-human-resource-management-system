import msal

from django.conf import settings
from django.db import transaction

from .models import ExternalIdentity, User


def get_entra_authority():
    """Return the Microsoft Entra ID authority URL."""
    return f"https://login.microsoftonline.com/{settings.ENTRA_TENANT_ID}"


def get_entra_msal_app():
    """Create the MSAL confidential client used by the SSO flow."""
    return msal.ConfidentialClientApplication(
        client_id=settings.ENTRA_CLIENT_ID,
        client_credential=settings.ENTRA_CLIENT_SECRET,
        authority=get_entra_authority(),
    )


def build_entra_authorization_url(state, nonce):
    """
    Build the Microsoft Entra ID authorization URL.

    State protects the authorization transaction against CSRF.
    Nonce binds the returned OIDC ID token to this login transaction.
    """
    app = get_entra_msal_app()

    return app.get_authorization_request_url(
        scopes=["openid", "profile", "email"],
        state=state,
        nonce=nonce,
        redirect_uri=settings.ENTRA_REDIRECT_URI,
        prompt="select_account",
    )


def exchange_entra_authorization_code(code):
    """
    Exchange an Entra authorization code for tokens and ID-token claims.
    """
    app = get_entra_msal_app()

    result = app.acquire_token_by_authorization_code(
        code,
        scopes=["openid", "profile", "email"],
        redirect_uri=settings.ENTRA_REDIRECT_URI,
    )

    if "error" in result:
        raise ValueError(
            result.get("error_description")
            or result.get("error")
            or "Microsoft Entra authentication failed."
        )

    return result


@transaction.atomic
def resolve_entra_user(claims):
    """
    Resolve an Entra identity to the authoritative HRMS User.

    The OIDC issuer + subject pair is the authoritative external
    identity key. Email is only provider metadata and is never used
    to silently create or select an HRMS account.
    """
    issuer = claims.get("iss")
    subject = claims.get("sub")

    if not issuer or not subject:
        raise ValueError("Required Entra identity claims are missing.")

    identity = (
        ExternalIdentity.objects
        .select_related("user")
        .filter(
            issuer=issuer,
            subject=subject,
        )
        .first()
    )

    if identity:
        user = identity.user

        if not user.is_active:
            raise ValueError("The linked HRMS account is inactive.")

        identity.email = claims.get("email") or claims.get("preferred_username", "")
        identity.display_name = claims.get("name", "")
        identity.save(update_fields=["email", "display_name", "updated_at"])

        return user

    raise ValueError(
        "This Microsoft Entra account is not linked to an HRMS user."
    )


def link_entra_identity(user, claims):
    """
    Explicitly link an already-authenticated HRMS user to an Entra identity.

    This function does not automatically create HRMS users.
    """
    issuer = claims.get("iss")
    subject = claims.get("sub")

    if not issuer or not subject:
        raise ValueError("Required Entra identity claims are missing.")

    existing = ExternalIdentity.objects.filter(
        issuer=issuer,
        subject=subject,
    ).first()

    if existing and existing.user_id != user.id:
        raise ValueError(
            "This Entra identity is already linked to another HRMS user."
        )

    identity, created = ExternalIdentity.objects.update_or_create(
        issuer=issuer,
        subject=subject,
        defaults={
            "user": user,
            "provider": "microsoft_entra_id",
            "email": claims.get("email") or claims.get("preferred_username", ""),
            "display_name": claims.get("name", ""),
        },
    )

    return identity, created

