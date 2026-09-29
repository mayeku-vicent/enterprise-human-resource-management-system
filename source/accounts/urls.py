from .sso_views import EntraLoginView, EntraCallbackView
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, PasswordChangeView, LogoutView
from .mfa_views import (
    MFAEnrollmentView,
    MFAEnrollmentConfirmView,
    MFAStatusView,
    MFARecoveryCodesView,
    MFAVerificationView,
)


router = DefaultRouter()

router.register(
    r"users",
    UserViewSet,
    basename="user"
)

urlpatterns = [
    path("", include(router.urls)),

    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="password-change",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    path(
        "mfa/enroll/",
        MFAEnrollmentView.as_view(),
        name="mfa-enroll",
    ),

    path(
        "mfa/enroll/confirm/",
        MFAEnrollmentConfirmView.as_view(),
        name="mfa-enroll-confirm",
    ),
   
    path(
        "mfa/status/",
        MFAStatusView.as_view(),
        name="mfa-status",
    ),

    path(
        "mfa/recovery-codes/",
        MFARecoveryCodesView.as_view(),
        name="mfa-recovery-codes",
    ),

    path("mfa/verify/", MFAVerificationView.as_view(), name="mfa-verify"),
    path(
    "sso/entra/login/",
    EntraLoginView.as_view(),
    name="entra-login",
   ),

   path(
    "sso/entra/callback/",
    EntraCallbackView.as_view(),
    name="entra-callback",
  ),
]


