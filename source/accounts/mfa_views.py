from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from config.authentication import SecureTokenObtainPairSerializer
from .mfa_services import complete_mfa_challenge

from .mfa_services import (
    begin_mfa_enrollment,
    confirm_mfa_enrollment,
    generate_recovery_codes,
    get_totp_device,
    complete_mfa_challenge,
)
from config.security import get_client_ip


class MFAEnrollmentView(APIView):
    """
    Start TOTP MFA enrollment for the currently authenticated user.

    Returns the provisioning URI and manual secret required to
    configure an authenticator application.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        device = begin_mfa_enrollment(user)

        return Response(
            {
                "detail": (
                    "MFA enrollment started. Configure your "
                    "authenticator application using the provisioning "
                    "URI or manual secret, then confirm the generated "
                    "verification code."
                ),
                "mfa_enabled": False,
                "device_id": device.id,
                "secret": device.key,
                "provisioning_uri": device.config_url,
            },
            status=status.HTTP_201_CREATED,
        )


class MFAEnrollmentConfirmView(APIView):
    """
    Confirm a TOTP MFA enrollment.

    A valid authenticator code permanently confirms the newly
    enrolled TOTP device and generates recovery codes.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        token = str(request.data.get("token", "")).strip()

        if not token:
            return Response(
                {"detail": "TOTP verification token is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        device = get_totp_device(request.user)

        if device is None:
            # The confirmed-device lookup intentionally does not find
            # the unconfirmed enrollment device, so locate the user's
            # most recent unconfirmed TOTP device directly.
            from django_otp.plugins.otp_totp.models import TOTPDevice

            device = (
                TOTPDevice.objects
                .filter(
                    user=request.user,
                    confirmed=False,
                )
                .order_by("-created_at")
                .first()
            )

        if device is None:
            return Response(
                {
                    "detail": (
                        "No pending MFA enrollment was found. "
                        "Start MFA enrollment first."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            confirmed = confirm_mfa_enrollment(
                request.user,
                device,
                token,
                request=request,
            )
        except ValueError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not confirmed:
            return Response(
                {
                    "detail": (
                        "The supplied TOTP verification code is invalid."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        recovery_codes = generate_recovery_codes(request.user)

        return Response(
            {
                "detail": (
                    "MFA enrollment confirmed successfully. "
                    "Save the recovery codes in a secure location."
                ),
                "mfa_enabled": True,
                "recovery_codes": recovery_codes,
            },
            status=status.HTTP_200_OK,
        )


class MFAStatusView(APIView):
    """
    Return the current MFA enrollment status for the authenticated user.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        device = get_totp_device(request.user)

        return Response(
            {
                "mfa_enabled": device is not None,
                "totp_enrolled": device is not None,
            },
            status=status.HTTP_200_OK,
        )


class MFARecoveryCodesView(APIView):
    """
    Generate a fresh set of MFA recovery codes.

    Existing unused recovery codes are replaced.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if get_totp_device(request.user) is None:
            return Response(
                {
                    "detail": (
                        "MFA must be enrolled before recovery codes "
                        "can be generated."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        recovery_codes = generate_recovery_codes(request.user)

        return Response(
            {
                "detail": (
                    "New MFA recovery codes generated successfully. "
                    "Previous unused recovery codes are no longer valid."
                ),
                "recovery_codes": recovery_codes,
            },
            status=status.HTTP_200_OK,
        )

class MFAVerificationView(APIView):
    """
    Complete an MFA login challenge using either a TOTP token
    or a recovery code, then issue the normal HRMS JWT pair.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        challenge = str(
            request.data.get("mfa_challenge", "")
        ).strip()

        token = str(
            request.data.get("token", "")
        ).strip()

        recovery_code = str(
            request.data.get("recovery_code", "")
        ).strip()

        if not challenge:
            return Response(
                {"detail": "MFA challenge is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if bool(token) == bool(recovery_code):
            return Response(
                {
                    "detail": (
                        "Provide exactly one second factor: "
                        "either a TOTP token or a recovery code."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = complete_mfa_challenge(
            raw_challenge=challenge,
            token=token or None,
            recovery_code=recovery_code or None,
            request=request,
        )

        if user is None:
            return Response(
                {
                    "detail": (
                        "The MFA challenge or second-factor "
                        "verification is invalid, expired, or already used."
                    )
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = SecureTokenObtainPairSerializer().get_token(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "mfa_required": False,
            },
            status=status.HTTP_200_OK,
        )

