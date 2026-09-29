from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class SecureJWTAuthentication(JWTAuthentication):
    """
    JWT authentication with per-user token-version validation.

    A token becomes invalid when the user's token_version changes.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)

        token_version = validated_token.get("token_version")

        if token_version is None:
            raise AuthenticationFailed(
                "Token security version is missing.",
                code="token_version_missing",
            )

        if token_version != user.token_version:
            raise AuthenticationFailed(
                "This session is no longer valid. Please authenticate again.",
                code="token_version_invalid",
            )

        return user
