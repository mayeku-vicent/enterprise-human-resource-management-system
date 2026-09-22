from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Attendance, ExpenseClaim
from accounts.models import EmployeeProfile
from leave.models import LeaveRequest
from .serializers import EmployeeProfileSerializer, AttendanceSerializer, ExpenseClaimSerializer
from leave.serializers import LeaveRequestSerializer

# New module models & serializers for Employee 360 aggregation
from assets.models import CompanyAsset
from assets.serializers import CompanyAssetSerializer
from performance.models import PerformanceGoal, Appraisal
from performance.serializers import PerformanceGoalSerializer, AppraisalSerializer
from training.models import EmployeeCertification
from training.serializers import EmployeeCertificationSerializer
from attendance_shifts.models import EmployeeShiftAssignment
from attendance_shifts.serializers import EmployeeShiftAssignmentSerializer

User = get_user_model()


class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.all().order_by('user__username')
    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-date', '-check_in_time')
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {"detail": "You have already checked in for today!"},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        today = timezone.now().date()
        try:
            attendance = Attendance.objects.get(employee=request.user, date=today)
            attendance.check_out_time = timezone.now().time()
            attendance.save()
            return Response({'status': 'Checked out successfully'}, status=status.HTTP_200_OK)
        except Attendance.DoesNotExist:
            return Response({'error': 'No check-in record found for today.'}, status=status.HTTP_400_BAD_REQUEST)


class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all().order_by('-created_at')
    serializer_class = ExpenseClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        claim = self.get_object()
        claim.status = ExpenseClaim.Status.APPROVED
        claim.save()
        return Response({'status': 'Claim Approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def mark_paid(self, request, pk=None):
        claim = self.get_object()
        claim.status = ExpenseClaim.Status.PAID
        claim.save()
        return Response({'status': 'Claim Marked as Paid'}, status=status.HTTP_200_OK)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-created_at')
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        leave_req = self.get_object()
        leave_req.status = 'APPROVED'
        leave_req.save()
        return Response({'status': 'Leave Request Approved'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        leave_req = self.get_object()
        leave_req.status = 'REJECTED'
        leave_req.save()
        return Response({'status': 'Leave Request Rejected'}, status=status.HTTP_200_OK)


class Employee360DetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)
        profile = EmployeeProfile.objects.filter(user=target_user).first()
        
        attendances = Attendance.objects.filter(employee=target_user).order_by('-date')[:10]
        claims = ExpenseClaim.objects.filter(employee=target_user).order_by('-created_at')
        leaves = LeaveRequest.objects.filter(employee=target_user).order_by('-created_at')
        
        assets = CompanyAsset.objects.filter(assigned_to=target_user)
        goals = PerformanceGoal.objects.filter(employee=target_user)
        appraisals = Appraisal.objects.filter(employee=target_user)
        certifications = EmployeeCertification.objects.filter(employee=target_user)
        shifts = EmployeeShiftAssignment.objects.filter(employee=target_user).order_by('-assigned_date')

        data = {
            "user_id": target_user.id,
            "username": target_user.username,
            "email": target_user.email,
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "profile": EmployeeProfileSerializer(profile).data if profile else None,
            "attendance_history": AttendanceSerializer(attendances, many=True).data,
            "expense_claims": ExpenseClaimSerializer(claims, many=True).data,
            "leave_requests": LeaveRequestSerializer(leaves, many=True).data,
            "assets": CompanyAssetSerializer(assets, many=True).data,
            "performance_goals": PerformanceGoalSerializer(goals, many=True).data,
            "appraisals": AppraisalSerializer(appraisals, many=True).data,
            "certifications": EmployeeCertificationSerializer(certifications, many=True).data,
            "shift_assignments": EmployeeShiftAssignmentSerializer(shifts, many=True).data,
        }
        return Response(data)


# Dashboard Template Views
@login_required
def employee_portal_dashboard(request):
    user = request.user
    assets = CompanyAsset.objects.filter(assigned_to=user)
    goals = PerformanceGoal.objects.filter(employee=user)
    certifications = EmployeeCertification.objects.filter(employee=user)

    context = {
        'assets': assets,
        'goals': goals,
        'certifications': certifications,
    }
    return render(request, 'hrms_modules/employee_portal.html', context)


def attendance_dashboard_view(request):
    return render(request, 'attendance_dashboard.html')


def claims_dashboard_view(request):
    return render(request, 'claims_dashboard.html')


def employee_360_view(request, user_id):
    return render(request, 'employee_360.html', {'target_user_id': user_id})