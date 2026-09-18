from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from config.views import api_root

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('admin/')),
    path('api/', api_root, name='api-root'), 
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/organization/', include('organization.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/leave/', include('leave.urls')),
    path('api/claims/', include('claims.urls')),
]