from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    employee_portal_dashboard,
    EmployeeProfileViewSet,
    AttendanceViewSet,
    ExpenseClaimViewSet,
    LeaveRequestViewSet,
    Employee360DetailView
)

router = DefaultRouter()
router.register(r'employees', EmployeeProfileViewSet, basename='employee')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'claims', ExpenseClaimViewSet, basename='claim')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-request')

urlpatterns = [
    path('', include(router.urls)),
    path('employee-360/<int:user_id>/', Employee360DetailView.as_view(), name='employee-360'),
    path('portal/', employee_portal_dashboard, name='employee-portal'),
]
