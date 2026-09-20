from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.views.generic import TemplateView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from claims.views import dashboard_view
from leave.views import leave_dashboard_view
from hrms_modules.views import (
    attendance_dashboard_view, 
    claims_dashboard_view, 
    employee_360_view 
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('admin/')),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('leave-dashboard/', leave_dashboard_view, name='leave-dashboard'),
    path('attendance-dashboard/', attendance_dashboard_view, name='attendance-dashboard'),
    path('claims-dashboard/', claims_dashboard_view, name='claims-dashboard'),
    path('employee-360/<int:user_id>/', employee_360_view, name='employee-360-ui'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/organization/', include('organization.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/leave/', include('leave.urls')),
    path('api/claims/', include('claims.urls')),
    path('claims/', include('claims.urls')),
    path('api/', include('hrms_modules.urls')),
]