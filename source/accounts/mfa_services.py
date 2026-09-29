import secrets

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from compliance.models import AuditLog
from config.security import get_client_ip
from django_otp.plugins.otp_totp.models import TOTPDevice

from .models import MFAChallenge, MFARecoveryCode, MFAPolicy


RECOVERY_CODE_COUNT = 10
RECOVERY_CODE_LENGTH = 10


def get_mfa_policy():
    """Return the single HRMS MFA policy."""
    policy, _ = MFAPolicy.objects.get_or_create(
        pk=1,
        defaults={"enforcement_mode": MFAPolicy.OPTIONAL},
    )
    return policy


def is_mfa_required(user):
    """Return whether MFA is required by the current HRMS policy."""
    policy = get_mfa_policy()
    return policy.enforcement_mode == MFAPolicy.REQUIRED


def get_totp_device(user):
    """Return the confirmed HRMS TOTP device for a user, if one exists."""
    return (
        TOTPDevice.objects
        .filter(user=user, confirmed=True)
        .order_by("-created_at")
        .first()
    )


def begin_mfa_enrollment(user):
    """
    Create an unconfirmed TOTP device for MFA enrollment.

    Existing unconfirmed devices are removed so an incomplete enrollment
    cannot leave multiple active enrollment secrets behind.
    """
    TOTPDevice.objects.filter(user=user, confirmed=False).delete()

    device = TOTPDevice.objects.create(
        user=user,
        name="HRMS Authenticator",
        confirmed=False,
    )

    AuditLog.objects.create(
        user=user,
        action="MFA_ENROLLMENT_STARTED",
        description="MFA enrollment was started and a new TOTP device was created.",
    )

    return device


def confirm_mfa_enrollment(user, device, token, request=None):
    """
    Verify the first TOTP code and confirm the device.
    """
    if device.user_id != user.id:
        raise ValueError("The MFA device does not belong to this user.")

    if device.confirmed:
        raise ValueError("The MFA device is already confirmed.")

    if not device.verify_token(str(token)):
        AuditLog.objects.create(
            user=user,
            action="MFA_ENROLLMENT_FAILED",
            description="MFA enrollment confirmation failed because the supplied TOTP code was invalid.",
        )
        return False

    device.confirmed = True
    device.save(update_fields=["confirmed", "last_used_at"])

    AuditLog.objects.create(
        user=user,
        action="MFA_ENROLLED",
        description="A TOTP authenticator was successfully enrolled and confirmed.",
    )

    return True


def verify_totp(user, token):
    """
    Verify a TOTP code against the user's confirmed device.
    """
    device = get_totp_device(user)

    if device is None:
        return False

    verified = device.verify_token(str(token))

    AuditLog.objects.create(
        user=user,
        action="MFA_VERIFICATION_SUCCESS" if verified else "MFA_VERIFICATION_FAILED",
        description=(
            "MFA TOTP verification succeeded."
            if verified
            else "MFA TOTP verification failed because the supplied code was invalid."
        ),
    )

    return verified


def generate_recovery_codes(user):
    """
    Replace the user's existing recovery codes with a new set.

    Only hashes are stored in the database.
    """
    codes = []

    for _ in range(RECOVERY_CODE_COUNT):
        raw_code = secrets.token_hex(RECOVERY_CODE_LENGTH // 2).upper()
        codes.append(raw_code)

    with transaction.atomic():
        MFARecoveryCode.objects.filter(
            user=user,
            used_at__isnull=True,
        ).delete()

        MFARecoveryCode.objects.bulk_create(
            [
                MFARecoveryCode(
                    user=user,
                    code_hash=make_password(code),
                )
                for code in codes
            ]
        )

    AuditLog.objects.create(
        user=user,
        action="MFA_RECOVERY_CODES_GENERATED",
        description=(
            f"{RECOVERY_CODE_COUNT} new MFA recovery codes were generated. "
            "Only hashed recovery codes are stored by the system."
        ),
    )

    return codes


def use_recovery_code(user, raw_code):
    """
    Atomically consume one unused recovery code.
    """
    candidates = (
        MFARecoveryCode.objects
        .select_for_update()
        .filter(user=user, used_at__isnull=True)
        .order_by("created_at")
    )

    with transaction.atomic():
        for recovery_code in candidates:
            if check_password(raw_code, recovery_code.code_hash):
                recovery_code.used_at = timezone.now()
                recovery_code.save(update_fields=["used_at"])

                AuditLog.objects.create(
                    user=user,
                    action="MFA_RECOVERY_CODE_USED",
                    description="A single-use MFA recovery code was successfully consumed.",
                )

                return True

    AuditLog.objects.create(
        user=user,
        action="MFA_RECOVERY_CODE_FAILED",
        description="An MFA recovery-code attempt failed because the supplied code was invalid or already used.",
    )

    return False


MFA_CHALLENGE_LIFETIME_MINUTES = 5


def create_mfa_challenge(user):
    """
    Create a short-lived MFA challenge.

    The raw challenge token is returned to the caller, while only its
    hash is stored in the database.
    """
    from django.utils.crypto import salted_hmac

    raw_challenge = secrets.token_urlsafe(32)
    challenge_hash = salted_hmac(
        "hrms-mfa-challenge",
        raw_challenge,
    ).hexdigest()

    expires_at = timezone.now() + timezone.timedelta(
        minutes=MFA_CHALLENGE_LIFETIME_MINUTES
    )

    MFAChallenge.objects.filter(
        user=user,
        used_at__isnull=True,
    ).update(
        used_at=timezone.now()
    )

    challenge = MFAChallenge.objects.create(
        user=user,
        challenge_hash=challenge_hash,
        expires_at=expires_at,
    )

    AuditLog.objects.create(
        user=user,
        action="MFA_CHALLENGE_CREATED",
        description="A short-lived MFA authentication challenge was created after successful password authentication.",
    )

    return raw_challenge, challenge


def consume_mfa_challenge(user, raw_challenge):
    """
    Validate and atomically consume a single-use MFA challenge.
    """
    from django.utils.crypto import salted_hmac

    if not raw_challenge:
        return False

    challenge_hash = salted_hmac(
        "hrms-mfa-challenge",
        raw_challenge,
    ).hexdigest()

    with transaction.atomic():
        challenge = (
            MFAChallenge.objects
            .select_for_update()
            .filter(
                user=user,
                challenge_hash=challenge_hash,
                used_at__isnull=True,
            )
            .first()
        )

        if challenge is None:
            return False

        if challenge.expires_at <= timezone.now():
            return False

        challenge.used_at = timezone.now()
        challenge.save(update_fields=["used_at"])

    AuditLog.objects.create(
        user=user,
        action="MFA_CHALLENGE_CONSUMED",
        description="A valid MFA authentication challenge was consumed successfully.",
    )

    return True

def complete_mfa_challenge(raw_challenge, token=None, recovery_code=None, request=None):
    """
    Verify a short-lived MFA login challenge together with a valid
    TOTP token or recovery code.

    The challenge is consumed only after the second factor succeeds.
    Returns the authenticated user on success, otherwise None.
    """
    from django.utils.crypto import salted_hmac

    if not raw_challenge:
        return None

    if bool(token) == bool(recovery_code):
        return None

    challenge_hash = salted_hmac(
        "hrms-mfa-challenge",
        raw_challenge,
    ).hexdigest()

    with transaction.atomic():
        challenge = (
            MFAChallenge.objects
            .select_for_update()
            .select_related("user")
            .filter(
                challenge_hash=challenge_hash,
                used_at__isnull=True,
            )
            .first()
        )

        if challenge is None:
            return None

        now = timezone.now()

        if challenge.expires_at <= now:
            return None

        user = challenge.user

        if not user.is_active:
            return None

        factor_valid = False

        if token:
            factor_valid = verify_totp(user, str(token).strip())
        elif recovery_code:
            factor_valid = use_recovery_code(
                user,
                str(recovery_code).strip(),
            )

        if not factor_valid:
            return None

        challenge.used_at = now
        challenge.save(update_fields=["used_at"])

        AuditLog.objects.create(
            user=user,
            action="MFA_CHALLENGE_CONSUMED",
            ip_address=get_client_ip(request) if request else None,
            description="A valid MFA authentication challenge was completed after successful second-factor verification.",
        )

        return user
