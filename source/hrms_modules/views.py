from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import get_user_model  # <-- 1. Import get_user_model
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import EmployeeProfile, Attendance, ExpenseClaim
from leave.models import LeaveRequest
from .serializers import EmployeeProfileSerializer, AttendanceSerializer, ExpenseClaimSerializer
from leave.serializers import LeaveRequestSerializer

User = get_user_model()  # <-- 2. Dynamically assign your custom User model


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


# --- Employee 360 Unified Profile View ---
class Employee360DetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        target_user = get_object_or_404(User, id=user_id)  # Queries 'accounts_user' safely
        profile = EmployeeProfile.objects.filter(user=target_user).first()
        
        attendances = Attendance.objects.filter(employee=target_user).order_by('-date')[:10]
        claims = ExpenseClaim.objects.filter(employee=target_user).order_by('-created_at')
        leaves = LeaveRequest.objects.filter(employee=target_user).order_by('-created_at')

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
        }
        return Response(data)


# Dashboard template views
def attendance_dashboard_view(request):
    return render(request, 'attendance_dashboard.html')


def claims_dashboard_view(request):
    return render(request, 'claims_dashboard.html')


def employee_360_view(request, user_id):
    return render(request, 'employee_360.html', {'target_user_id': user_id})