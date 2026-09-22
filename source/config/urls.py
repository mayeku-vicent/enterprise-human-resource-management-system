from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Existing UI views
from hrms_modules.dashboard_views import central_dashboard_view
from leave.views import leave_dashboard_view
from hrms_modules.views import (
    attendance_dashboard_view,
    claims_dashboard_view,
    employee_360_view,
    employee_directory_view,
)

# New API ViewSets
from rest_framework.routers import DefaultRouter
from assets.views import CompanyAssetViewSet
from performance.views import PerformanceGoalViewSet, AppraisalViewSet
from training.views import TrainingCourseViewSet, EmployeeCertificationViewSet
from attendance_shifts.views import WorkShiftViewSet, EmployeeShiftAssignmentViewSet


# Setup the DRF router for our new modules
router = DefaultRouter()
router.register(r'assets', CompanyAssetViewSet)
router.register(r'performance-goals', PerformanceGoalViewSet)
router.register(r'appraisals', AppraisalViewSet)
router.register(r'training-courses', TrainingCourseViewSet)
router.register(r'certifications', EmployeeCertificationViewSet)
router.register(r'work-shifts', WorkShiftViewSet)
router.register(r'shift-assignments', EmployeeShiftAssignmentViewSet)


urlpatterns = [
    # Admin and Authentication
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),

    # Root Redirect
    path('', lambda request: redirect('dashboard')),

    # UI Dashboards
    path('dashboard/', central_dashboard_view, name='dashboard'),
    path('leave-dashboard/', leave_dashboard_view, name='leave-dashboard'),
    path('attendance-dashboard/', attendance_dashboard_view, name='attendance-dashboard'),
    path('claims-dashboard/', claims_dashboard_view, name='claims-dashboard'),
    path('employee-360/<int:user_id>/', employee_360_view, name='employee-360-ui'),
    path('employees/', employee_directory_view, name='employee-directory'),

    # JWT Authentication APIs
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Existing App APIs
    path('api/organization/', include('organization.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/leave/', include('leave.urls')),
    path('api/claims/', include('claims.urls')),
    path('claims/', include('claims.urls')),
    path('api/', include('hrms_modules.urls')),

    # New Module API Endpoints
    path('api/', include(router.urls)),
]