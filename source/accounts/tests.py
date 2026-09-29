from compliance.models import AuditLog
from accounts.models import EmployeeProfile, User
from organization.models import Branch, Company, Location
from django.test import TestCase

# Create your tests here.

class EmployeeOrganizationLocationTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(
            name="Test Company",
            code="TC",
        )
        self.branch = Branch.objects.create(
            company=self.company,
            name="Main Branch",
            code="MAIN",
        )
        self.location = Location.objects.create(
            branch=self.branch,
            name="Head Office",
            code="HQ",
            address="Test Address",
        )

        self.user = User.objects.create_user(
            username="employee-location-test",
            password="TestPassword123!",
        )

    def test_employee_can_have_authoritative_organization_location(self):
        profile = EmployeeProfile.objects.create(
            user=self.user,
            organization_location=self.location,
        )

        profile.refresh_from_db()

        self.assertEqual(
            profile.organization_location_id,
            self.location.id,
        )
        self.assertEqual(
            profile.organization_location.name,
            "Head Office",
        )

    def test_organization_location_is_optional(self):
        profile = EmployeeProfile.objects.create(
            user=self.user,
        )

        self.assertIsNone(profile.organization_location)

    def test_legacy_location_field_is_preserved(self):
        profile = EmployeeProfile.objects.create(
            user=self.user,
            location="Old Location Text",
        )

        profile.refresh_from_db()

        self.assertEqual(profile.location, "Old Location Text")
        self.assertIsNone(profile.organization_location)


class LogoutAPITests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken

        self.User = get_user_model()
        self.APIClient = APIClient
        self.RefreshToken = RefreshToken

        self.user = self.User.objects.create_user(
            username="logout_test_user",
            password="TestPassword123!",
        )

        self.other_user = self.User.objects.create_user(
            username="other_logout_user",
            password="TestPassword123!",
        )

        self.client = self.APIClient()
        self.client.force_authenticate(user=self.user)

    def test_authenticated_user_can_logout(self):
        refresh = self.RefreshToken.for_user(self.user)

        response = self.client.post(
            "/api/accounts/logout/",
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["detail"], "Logout successful.")

        from rest_framework_simplejwt.token_blacklist.models import (
            BlacklistedToken,
        )

        self.assertTrue(
            BlacklistedToken.objects.filter(
                token__jti=refresh["jti"]
            ).exists()
        )

        from compliance.models import AuditLog

        self.assertTrue(
            AuditLog.objects.filter(
                user=self.user,
                action="LOGOUT",
            ).exists()
        )

    def test_logout_requires_refresh_token(self):
        response = self.client.post(
            "/api/accounts/logout/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Refresh token is required.",
        )

    def test_user_cannot_logout_with_another_users_refresh_token(self):
        refresh = self.RefreshToken.for_user(self.other_user)

        response = self.client.post(
            "/api/accounts/logout/",
            {"refresh": str(refresh)},
            format="json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.data["detail"],
            "The refresh token does not belong to the authenticated user.",
        )

    def test_logout_rejects_invalid_refresh_token(self):
        response = self.client.post(
            "/api/accounts/logout/",
            {"refresh": "invalid-refresh-token"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Invalid or already blacklisted refresh token.",
        )

class MFAAPITests(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        from django.contrib.auth import get_user_model
        from .models import MFAPolicy

        self.client = APIClient()
        self.User = get_user_model()

        self.user = self.User.objects.create_user(
            username="mfa_api_test_user",
            password="TestPassword123!",
        )

        self.client.force_authenticate(user=self.user)

        MFAPolicy.objects.update_or_create(
            pk=1,
            defaults={"enforcement_mode": MFAPolicy.OPTIONAL},
        )

    def test_mfa_status_initially_disabled(self):
        response = self.client.get("/api/accounts/mfa/status/")

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.data["mfa_enabled"])
        self.assertFalse(response.data["totp_enrolled"])

    def test_authenticated_user_can_start_mfa_enrollment(self):
        response = self.client.post("/api/accounts/mfa/enroll/")

        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data["mfa_enabled"])
        self.assertIn("device_id", response.data)
        self.assertIn("secret", response.data)
        self.assertIn("provisioning_uri", response.data)

    def test_mfa_enrollment_requires_authentication(self):
        self.client.force_authenticate(user=None)

        response = self.client.post("/api/accounts/mfa/enroll/")

        self.assertEqual(response.status_code, 401)
    def test_mfa_enrollment_can_be_confirmed_with_valid_totp(self):
        from django_otp.oath import totp
        from django_otp.plugins.otp_totp.models import TOTPDevice

        enrollment_response = self.client.post(
            "/api/accounts/mfa/enroll/"
        )

        self.assertEqual(enrollment_response.status_code, 201)

        device_id = enrollment_response.data["device_id"]

        device = TOTPDevice.objects.get(
            id=device_id,
            user=self.user,
        )

        token = str(
            totp(
                device.bin_key,
                step=device.step,
                t0=device.t0,
                digits=device.digits,
            )
        )

        response = self.client.post(
            "/api/accounts/mfa/enroll/confirm/",
            {"token": token},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["mfa_enabled"])
        self.assertEqual(len(response.data["recovery_codes"]), 10)

        device.refresh_from_db()

        self.assertTrue(device.confirmed)

    def test_mfa_enrollment_rejects_invalid_totp(self):
        self.client.post("/api/accounts/mfa/enroll/")

        response = self.client.post(
            "/api/accounts/mfa/enroll/confirm/",
            {"token": "000000"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
class MFALoginVerificationTests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from django_otp.plugins.otp_totp.models import TOTPDevice
        from rest_framework.test import APIClient

        from .models import MFAPolicy
        from .mfa_services import create_mfa_challenge

        self.client = APIClient()
        self.User = get_user_model()
        self.create_mfa_challenge = create_mfa_challenge
        self.TOTPDevice = TOTPDevice

        self.user = self.User.objects.create_user(
            username="mfa_login_test_user",
            password="TestPassword123!",
        )

        MFAPolicy.objects.update_or_create(
            pk=1,
            defaults={"enforcement_mode": MFAPolicy.REQUIRED},
        )

        self.device = TOTPDevice.objects.create(
            user=self.user,
            name="Test Authenticator",
            confirmed=True,
        )

    def _create_challenge(self):
        raw_challenge, challenge = self.create_mfa_challenge(self.user)
        return raw_challenge, challenge

    def _current_totp(self):
        from django_otp.oath import totp

        return str(
            totp(
                self.device.bin_key,
                step=self.device.step,
                t0=self.device.t0,
                digits=self.device.digits,
            )
        )

    def test_valid_totp_completes_mfa_login_and_returns_jwt(self):
        challenge, _ = self._create_challenge()
        token = self._current_totp()

        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "token": token,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertFalse(response.data["mfa_required"])

    def test_invalid_totp_does_not_consume_challenge(self):
        from .models import MFAChallenge

        challenge, challenge_record = self._create_challenge()

        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "token": "000000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

        challenge_record.refresh_from_db()
        self.assertIsNone(challenge_record.used_at)

    def test_consumed_challenge_cannot_be_reused(self):
        challenge, challenge_record = self._create_challenge()
        token = self._current_totp()

        first_response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "token": token,
            },
            format="json",
        )

        self.assertEqual(first_response.status_code, 200)

        challenge_record.refresh_from_db()
        self.assertIsNotNone(challenge_record.used_at)

        second_response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "token": token,
            },
            format="json",
        )

        self.assertEqual(second_response.status_code, 401)

    def test_expired_challenge_is_rejected(self):
        from datetime import timedelta
        from django.utils import timezone

        challenge, challenge_record = self._create_challenge()

        challenge_record.expires_at = timezone.now() - timedelta(seconds=1)
        challenge_record.save(update_fields=["expires_at"])

        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "token": self._current_totp(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

        challenge_record.refresh_from_db()
        self.assertIsNone(challenge_record.used_at)

    def test_recovery_code_can_complete_mfa_login(self):
        from .mfa_services import generate_recovery_codes

        challenge, _ = self._create_challenge()
        recovery_codes = generate_recovery_codes(self.user)

        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "recovery_code": recovery_codes[0],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_used_recovery_code_cannot_complete_another_challenge(self):
        from .mfa_services import generate_recovery_codes

        recovery_codes = generate_recovery_codes(self.user)
        recovery_code = recovery_codes[0]

        first_challenge, _ = self._create_challenge()

        first_response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": first_challenge,
                "recovery_code": recovery_code,
            },
            format="json",
        )

        self.assertEqual(first_response.status_code, 200)

        second_challenge, _ = self._create_challenge()

        second_response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": second_challenge,
                "recovery_code": recovery_code,
            },
            format="json",
        )

        self.assertEqual(second_response.status_code, 401)

    def test_mfa_verification_requires_exactly_one_second_factor(self):
        challenge, _ = self._create_challenge()

        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": challenge,
                "token": "000000",
                "recovery_code": "ABCDEF1234",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)

    def test_unknown_challenge_is_rejected(self):
        response = self.client.post(
            "/api/accounts/mfa/verify/",
            {
                "mfa_challenge": "invalid-challenge-token",
                "token": "000000",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)

from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from .models import ExternalIdentity, User


class EntraSSOTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="sso_test_user",
            password="StrongTestPassword123!",
            email="sso_test@example.com",
        )

    def test_entra_login_requires_no_authentication(self):
        with patch(
            "accounts.sso_views.build_entra_authorization_url",
            return_value="https://login.example.com/authorize",
        ):
            response = self.client.get(
                reverse("entra-login"),
                follow=False,
            )

        self.assertEqual(response.status_code, 302)

    def test_entra_login_stores_state(self):
        with patch(
            "accounts.sso_views.build_entra_authorization_url",
            return_value="https://login.example.com/authorize",
        ):
            response = self.client.get(
                reverse("entra-login"),
                follow=False,
            )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response["Location"],
            "https://login.example.com/authorize",
        )
        self.assertTrue(
            self.client.session.get("entra_sso_state")
        )

    def test_callback_rejects_invalid_state(self):
        session = self.client.session
        session["entra_sso_state"] = "expected-state"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "wrong-state",
                "code": "fake-code",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_callback_requires_authorization_code(self):
        session = self.client.session
        session["entra_sso_state"] = "expected-state"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "expected-state",
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_existing_external_identity_resolves_user(self):
        ExternalIdentity.objects.create(
            user=self.user,
            provider="microsoft_entra_id",
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="test-subject-001",
            email="sso_test@example.com",
            display_name="SSO Test User",
        )

        from .sso_services import resolve_entra_user

        resolved_user = resolve_entra_user(
            {
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": "test-subject-001",
                "email": "updated@example.com",
                "name": "Updated SSO User",
            }
        )

        self.assertEqual(resolved_user.pk, self.user.pk)

        identity = ExternalIdentity.objects.get(
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="test-subject-001",
        )

        self.assertEqual(identity.email, "updated@example.com")
        self.assertEqual(identity.display_name, "Updated SSO User")

    def test_unlinked_external_identity_is_rejected(self):
        from .sso_services import resolve_entra_user

        with self.assertRaisesMessage(
            ValueError,
            "This Microsoft Entra account is not linked to an HRMS user.",
        ):
            resolve_entra_user(
                {
                    "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                    "sub": "unknown-subject",
                    "email": "unknown@example.com",
                    "name": "Unknown User",
                "nonce": "valid-nonce",
                }
            )

    @patch("accounts.sso_views.exchange_entra_authorization_code")
    def test_callback_resolves_linked_user_and_returns_jwt(
        self,
        mock_exchange,
    ):
        ExternalIdentity.objects.create(
            user=self.user,
            provider="microsoft_entra_id",
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="linked-subject-001",
            email="sso_test@example.com",
            display_name="SSO Test User",
        )

        mock_exchange.return_value = {
            "id_token_claims": {
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": "linked-subject-001",
                "email": "sso_test@example.com",
                "name": "SSO Test User",
                "nonce": "valid-nonce",
            }
        }

        session = self.client.session
        session["entra_sso_state"] = "valid-state"
        session["entra_sso_nonce"] = "valid-nonce"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "valid-state",
                "code": "authorization-code",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["access"])
        self.assertTrue(response.data["refresh"])
        self.assertFalse(response.data["mfa_required"])
        self.assertEqual(
            response.data["sso_provider"],
            "microsoft_entra_id",
        )

        mock_exchange.assert_called_once_with("authorization-code")

    @patch("accounts.sso_views.exchange_entra_authorization_code")
    def test_callback_rejects_unlinked_identity(
        self,
        mock_exchange,
    ):
        mock_exchange.return_value = {
            "id_token_claims": {
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": "unlinked-subject-001",
                "email": "unknown@example.com",
                "name": "Unknown User",
                "nonce": "valid-nonce",
            }
        }

        session = self.client.session
        session["entra_sso_state"] = "valid-state"
        session["entra_sso_nonce"] = "valid-nonce"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "valid-state",
                "code": "authorization-code",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "not linked to an HRMS user",
            response.data["detail"],
        )

    def test_link_entra_identity_prevents_cross_user_linking(self):
        from .sso_services import link_entra_identity

        ExternalIdentity.objects.create(
            user=self.user,
            provider="microsoft_entra_id",
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="already-linked-subject",
        )

        another_user = User.objects.create_user(
            username="another_sso_user",
            password="AnotherStrongPassword123!",
        )

        with self.assertRaisesMessage(
            ValueError,
            "This Entra identity is already linked to another HRMS user.",
        ):
            link_entra_identity(
                another_user,
                {
                    "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                    "sub": "already-linked-subject",
                },
            )

    @patch("accounts.sso_views.create_mfa_challenge")
    @patch("accounts.sso_views.get_totp_device")
    @patch("accounts.sso_views.is_mfa_required", return_value=True)
    @patch("accounts.sso_views.exchange_entra_authorization_code")
    def test_callback_requires_mfa_before_jwt(
        self,
        mock_exchange,
        mock_is_mfa_required,
        mock_get_totp_device,
        mock_create_mfa_challenge,
    ):
        ExternalIdentity.objects.create(
            user=self.user,
            provider="microsoft_entra_id",
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="mfa-required-subject",
        )

        mock_exchange.return_value = {
            "id_token_claims": {
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": "mfa-required-subject",
                "email": "sso_test@example.com",
                "name": "SSO Test User",
                "nonce": "valid-nonce",
            }
        }

        mock_get_totp_device.return_value = object()
        mock_create_mfa_challenge.return_value = "test-mfa-challenge"

        session = self.client.session
        session["entra_sso_state"] = "valid-state"
        session["entra_sso_nonce"] = "valid-nonce"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "valid-state",
                "code": "authorization-code",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["mfa_required"])
        self.assertEqual(
            response.data["mfa_challenge"],
            "test-mfa-challenge",
        )
        self.assertEqual(
            response.data["sso_provider"],
            "microsoft_entra_id",
        )
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

        mock_is_mfa_required.assert_called_once_with(self.user)
        mock_get_totp_device.assert_called_once_with(self.user)
        mock_create_mfa_challenge.assert_called_once_with(self.user)

    @patch("accounts.sso_views.get_totp_device", return_value=None)
    @patch("accounts.sso_views.is_mfa_required", return_value=True)
    @patch("accounts.sso_views.exchange_entra_authorization_code")
    def test_callback_requires_mfa_enrollment(
        self,
        mock_exchange,
        mock_is_mfa_required,
        mock_get_totp_device,
    ):
        ExternalIdentity.objects.create(
            user=self.user,
            provider="microsoft_entra_id",
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="mfa-enrollment-required-subject",
        )

        mock_exchange.return_value = {
            "id_token_claims": {
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": "mfa-enrollment-required-subject",
                "email": "sso_test@example.com",
                "name": "SSO Test User",
                "nonce": "valid-nonce",
            }
        }

        session = self.client.session
        session["entra_sso_state"] = "valid-state"
        session["entra_sso_nonce"] = "valid-nonce"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "valid-state",
                "code": "authorization-code",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertTrue(response.data["mfa_required"])
        self.assertTrue(response.data["mfa_enrollment_required"])
        self.assertEqual(
            response.data["sso_provider"],
            "microsoft_entra_id",
        )
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)

        mock_is_mfa_required.assert_called_once_with(self.user)
        mock_get_totp_device.assert_called_once_with(self.user)





    @patch("accounts.sso_views.exchange_entra_authorization_code")
    def test_callback_rejects_invalid_nonce(self, mock_exchange):
        ExternalIdentity.objects.create(
            user=self.user,
            provider="microsoft_entra_id",
            issuer="https://login.microsoftonline.com/test-tenant/v2.0",
            subject="invalid-nonce-subject",
        )

        mock_exchange.return_value = {
            "id_token_claims": {
                "iss": "https://login.microsoftonline.com/test-tenant/v2.0",
                "sub": "invalid-nonce-subject",
                "email": "sso_test@example.com",
                "name": "SSO Test User",
                "nonce": "wrong-nonce",
            }
        }

        session = self.client.session
        session["entra_sso_state"] = "valid-state"
        session["entra_sso_nonce"] = "valid-nonce"
        session.save()

        response = self.client.get(
            reverse("entra-callback"),
            {
                "state": "valid-state",
                "code": "authorization-code",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["detail"],
            "Invalid or expired SSO nonce.",
        )
        self.assertNotIn("access", response.data)
        self.assertNotIn("refresh", response.data)


class SessionManagementAPITests(TestCase):
    def setUp(self):
        from django.contrib.auth import get_user_model
        from rest_framework.test import APIClient
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.token_blacklist.models import (
            OutstandingToken,
            BlacklistedToken,
        )

        self.User = get_user_model()
        self.APIClient = APIClient
        self.RefreshToken = RefreshToken
        self.OutstandingToken = OutstandingToken
        self.BlacklistedToken = BlacklistedToken
        self.admin = self.User.objects.create_superuser(
            username="session_admin",
            password="TestPassword123!",
        )

        self.admin.role = self.User.Role.ADMIN
        self.admin.save(update_fields=["role"])
       

        self.target_user = self.User.objects.create_user(
            username="session_target",
            password="TestPassword123!",
        )

        self.employee = self.User.objects.create_user(
            username="session_employee",
            password="TestPassword123!",
        )

        self.client = self.APIClient()

    def test_admin_can_view_user_sessions(self):
        refresh = self.RefreshToken.for_user(self.target_user)
        jti = str(refresh["jti"])

        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            f"/api/accounts/users/{self.target_user.id}/sessions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data["sessions"]) >= 1)

        session = next(
            item for item in response.data["sessions"]
            if item["jti"] == jti
        )

        self.assertEqual(session["status"], "OUTSTANDING")
        self.assertIn("created_at", session)
        self.assertIn("expires_at", session)

        self.assertNotIn("refresh", session)
        self.assertNotIn("access", session)

    def test_non_admin_cannot_view_user_sessions(self):
        self.client.force_authenticate(user=self.employee)

        response = self.client.get(
            f"/api/accounts/users/{self.target_user.id}/sessions/"
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_revoke_one_session(self):
        refresh = self.RefreshToken.for_user(self.target_user)
        jti = str(refresh["jti"])

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/accounts/users/{self.target_user.id}/sessions/{jti}/revoke/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["status"], "BLACKLISTED")

        token = self.OutstandingToken.objects.get(
            jti=jti,
            user=self.target_user,
        )

        self.assertTrue(
            self.BlacklistedToken.objects.filter(
                token=token
            ).exists()
        )

    def test_non_admin_cannot_revoke_one_session(self):
        refresh = self.RefreshToken.for_user(self.target_user)
        jti = str(refresh["jti"])

        self.client.force_authenticate(user=self.employee)

        response = self.client.post(
            f"/api/accounts/users/{self.target_user.id}/sessions/{jti}/revoke/"
        )

        self.assertEqual(response.status_code, 403)

    def test_admin_can_revoke_all_user_sessions(self):
        self.RefreshToken.for_user(self.target_user)
        self.RefreshToken.for_user(self.target_user)

        previous_token_version = self.target_user.token_version

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/accounts/users/{self.target_user.id}/revoke-sessions/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "All authentication sessions for the user have been revoked successfully.",
            response.data["detail"],
        )

        self.target_user.refresh_from_db()

        self.assertEqual(
            self.target_user.token_version,
            previous_token_version + 1,
        )

    def test_admin_cannot_revoke_own_sessions(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/accounts/users/{self.admin.id}/revoke-sessions/"
        )

        self.assertEqual(response.status_code, 400)





