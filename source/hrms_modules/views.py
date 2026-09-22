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

from accounts.models import (
    EmployeeProfile,
    EmploymentHistory,
    EmployeeContact,
    EmergencyContact,
)

from leave.models import LeaveRequest

from .serializers import (
    EmployeeProfileSerializer,
    AttendanceSerializer,
    ExpenseClaimSerializer,
    EmployeeSalarySerializer,
    PayslipSerializer,
    EmployeeDocumentSerializer,
    AuditLogSerializer,
)

from leave.serializers import LeaveRequestSerializer

# Employee 360 module models & serializers
from assets.models import CompanyAsset
from assets.serializers import CompanyAssetSerializer

from payroll.models import EmployeeSalary, Payslip
from documents.models import EmployeeDocument
from compliance.models import AuditLog

from performance.models import PerformanceGoal, Appraisal
from performance.serializers import (
    PerformanceGoalSerializer,
    AppraisalSerializer,
)

from training.models import EmployeeCertification
from training.serializers import EmployeeCertificationSerializer

from attendance_shifts.models import EmployeeShiftAssignment
from attendance_shifts.serializers import EmployeeShiftAssignmentSerializer


User = get_user_model()


# ============================================================
# EMPLOYEE PROFILE API
# ============================================================

class EmployeeProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployeeProfile.objects.all().order_by('user__username')
    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


# ============================================================
# ATTENDANCE API
# ============================================================

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by(
        '-date',
        '-check_in_time'
    )
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except IntegrityError:
            return Response(
                {
                    "detail": "You have already checked in for today!"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def check_out(self, request):
        today = timezone.now().date()

        try:
            attendance = Attendance.objects.get(
                employee=request.user,
                date=today
            )

            attendance.check_out_time = timezone.now().time()
            attendance.save()

            return Response(
                {
                    'status': 'Checked out successfully'
                },
                status=status.HTTP_200_OK
            )

        except Attendance.DoesNotExist:
            return Response(
                {
                    'error': 'No check-in record found for today.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================
# EXPENSE CLAIM API
# ============================================================

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all().order_by('-created_at')
    serializer_class = ExpenseClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        claim = self.get_object()

        claim.status = ExpenseClaim.Status.APPROVED
        claim.save()

        return Response(
            {
                'status': 'Claim Approved'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'])
    def mark_paid(self, request, pk=None):
        claim = self.get_object()

        claim.status = ExpenseClaim.Status.PAID
        claim.save()

        return Response(
            {
                'status': 'Claim Marked as Paid'
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# LEAVE REQUEST API
# ============================================================

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

        return Response(
            {
                'status': 'Leave Request Approved'
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        leave_req = self.get_object()

        leave_req.status = 'REJECTED'
        leave_req.save()

        return Response(
            {
                'status': 'Leave Request Rejected'
            },
            status=status.HTTP_200_OK
        )


# ============================================================
# EMPLOYEE 360 API
# ============================================================

class Employee360DetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, user_id):
        # ----------------------------------------------------
        # BASIC EMPLOYEE
        # ----------------------------------------------------

        target_user = get_object_or_404(
            User,
            id=user_id
        )

        profile = EmployeeProfile.objects.filter(
            user=target_user
        ).first()

        # ----------------------------------------------------
        # ATTENDANCE
        # ----------------------------------------------------

        attendances = Attendance.objects.filter(
            employee=target_user
        ).order_by('-date')[:10]

        # ----------------------------------------------------
        # EXPENSE CLAIMS
        # ----------------------------------------------------

        claims = ExpenseClaim.objects.filter(
            employee=target_user
        ).order_by('-created_at')

        # ----------------------------------------------------
        # LEAVE
        # ----------------------------------------------------

        leaves = LeaveRequest.objects.filter(
            employee=target_user
        ).order_by('-created_at')

        # ----------------------------------------------------
        # ASSETS
        # ----------------------------------------------------

        assets = CompanyAsset.objects.filter(
            assigned_to=target_user
        )

        # ----------------------------------------------------
        # PERFORMANCE
        # ----------------------------------------------------

        goals = PerformanceGoal.objects.filter(
            employee=target_user
        )

        appraisals = Appraisal.objects.filter(
            employee=target_user
        )

        # ----------------------------------------------------
        # TRAINING
        # ----------------------------------------------------

        certifications = EmployeeCertification.objects.filter(
            employee=target_user
        )

        # ----------------------------------------------------
        # SHIFT ASSIGNMENTS
        # ----------------------------------------------------

        shifts = EmployeeShiftAssignment.objects.filter(
            employee=target_user
        ).order_by('-assigned_date')
                # ----------------------------------------------------
        # COMPENSATION / SALARY
        # ----------------------------------------------------

        salary = (
            EmployeeSalary.objects.filter(
                employee=target_user
            ).first()
        )

        # ----------------------------------------------------
        # PAYROLL
        # ----------------------------------------------------

        payslips = Payslip.objects.filter(
            employee=target_user
        ).order_by('-generated_at')

        # ----------------------------------------------------
        # DOCUMENTS
        # ----------------------------------------------------

        documents = EmployeeDocument.objects.filter(
            employee=target_user
        ).order_by('-uploaded_at')

        # ----------------------------------------------------
        # AUDIT HISTORY
        # ----------------------------------------------------

        audit_history = AuditLog.objects.filter(
            user=target_user
        ).order_by('-timestamp')

        # ----------------------------------------------------
        # EMPLOYMENT HISTORY
        # ----------------------------------------------------

        employment_history = (
            EmploymentHistory.objects.filter(
                employee=profile
            )
            .select_related(
                'department',
                'position'
            )
            .order_by(
                '-start_date',
                '-created_at'
            )
            if profile
            else EmploymentHistory.objects.none()
        )

        # ----------------------------------------------------
        # EMPLOYEE CONTACTS
        # ----------------------------------------------------

        employee_contacts = (
            EmployeeContact.objects.filter(
                employee=profile
            )
            .order_by(
                '-is_primary',
                'id'
            )
            if profile
            else EmployeeContact.objects.none()
        )

        # ----------------------------------------------------
        # EMERGENCY CONTACTS
        # ----------------------------------------------------

        emergency_contacts = (
            EmergencyContact.objects.filter(
                employee=profile
            )
            .order_by(
                '-is_primary',
                'id'
            )
            if profile
            else EmergencyContact.objects.none()
        )

        # ----------------------------------------------------
        # EMPLOYEE 360 RESPONSE
        # ----------------------------------------------------

        data = {
            "user_id": target_user.id,

            "username": target_user.username,

            "email": target_user.email,

            "first_name": target_user.first_name,

            "last_name": target_user.last_name,

            # ------------------------------------------------
            # MASTER EMPLOYEE PROFILE
            # ------------------------------------------------

            "profile": (
                EmployeeProfileSerializer(profile).data
                if profile
                else None
            ),

            # ------------------------------------------------
            # ATTENDANCE
            # ------------------------------------------------

            "attendance_history": AttendanceSerializer(
                attendances,
                many=True
            ).data,

            # ------------------------------------------------
            # EXPENSE CLAIMS
            # ------------------------------------------------

            "expense_claims": ExpenseClaimSerializer(
                claims,
                many=True
            ).data,

            # ------------------------------------------------
            # LEAVE
            # ------------------------------------------------

            "leave_requests": LeaveRequestSerializer(
                leaves,
                many=True
            ).data,

            # ------------------------------------------------
            # ASSETS
            # ------------------------------------------------

            "assets": CompanyAssetSerializer(
                assets,
                many=True
            ).data,

            # ------------------------------------------------
            # PERFORMANCE
            # ------------------------------------------------

            "performance_goals": PerformanceGoalSerializer(
                goals,
                many=True
            ).data,

            "appraisals": AppraisalSerializer(
                appraisals,
                many=True
            ).data,

            # ------------------------------------------------
            # TRAINING
            # ------------------------------------------------

            "certifications": EmployeeCertificationSerializer(
                certifications,
                many=True
            ).data,

            # ------------------------------------------------
            # SHIFT ASSIGNMENTS
            # ------------------------------------------------

            "shift_assignments": EmployeeShiftAssignmentSerializer(
                shifts,
                many=True
            ).data,
                       # ------------------------------------------------
            # COMPENSATION / SALARY
            # ------------------------------------------------

            "salary": (
                EmployeeSalarySerializer(salary).data
                if salary
                else None
            ),

            # ------------------------------------------------
            # PAYROLL
            # ------------------------------------------------

            "payslips": PayslipSerializer(
                payslips,
                many=True
            ).data,

            # ------------------------------------------------
            # DOCUMENTS
            # ------------------------------------------------

            "documents": EmployeeDocumentSerializer(
                documents,
                many=True
            ).data,

            # ------------------------------------------------
            # AUDIT HISTORY
            # ------------------------------------------------

            "audit_history": AuditLogSerializer(
                audit_history,
                many=True
            ).data,

            # ------------------------------------------------
            # EMPLOYMENT HISTORY
            # ------------------------------------------------

            "employment_history": [
                {
                    "id": record.id,
                    "employment_type": record.employment_type,
                    "employment_status": record.employment_status,
                    "job_title": record.job_title,

                    "department": (
                        record.department.name
                        if record.department
                        else None
                    ),

                    "position": (
                        record.position.title
                        if record.position
                        else None
                    ),

                    "start_date": record.start_date,

                    "end_date": record.end_date,

                    "reason": record.reason,

                    "notes": record.notes,
                }

                for record in employment_history
            ],

            # ------------------------------------------------
            # EMPLOYEE CONTACTS
            # ------------------------------------------------

            "employee_contacts": [
                {
                    "id": contact.id,
                    "contact_type": contact.contact_type,
                    "phone_number": contact.phone_number,
                    "alternate_phone": contact.alternate_phone,
                    "email": contact.email,
                    "address": contact.address,
                    "is_primary": contact.is_primary,
                }

                for contact in employee_contacts
            ],

            # ------------------------------------------------
            # EMERGENCY CONTACTS
            # ------------------------------------------------

            "emergency_contacts": [
                {
                    "id": contact.id,
                    "full_name": contact.full_name,
                    "relationship": contact.relationship,
                    "phone_number": contact.phone_number,
                    "alternate_phone": contact.alternate_phone,
                    "email": contact.email,
                    "address": contact.address,
                    "is_primary": contact.is_primary,
                }

                for contact in emergency_contacts
            ],
        }

        return Response(data)


# ============================================================
# DASHBOARD TEMPLATE VIEWS
# ============================================================

@login_required
def employee_portal_dashboard(request):
    user = request.user

    assets = CompanyAsset.objects.filter(
        assigned_to=user
    )

    goals = PerformanceGoal.objects.filter(
        employee=user
    )

    certifications = EmployeeCertification.objects.filter(
        employee=user
    )

    context = {
        'assets': assets,
        'goals': goals,
        'certifications': certifications,
    }

    return render(
        request,
        'hrms_modules/employee_portal.html',
        context
    )


def attendance_dashboard_view(request):
    return render(
        request,
        'attendance_dashboard.html'
    )


def claims_dashboard_view(request):
    return render(
        request,
        'claims_dashboard.html'
    )


@login_required
def employee_directory_view(request):
    return render(
        request,
        'employee_directory.html'
    )


def employee_360_view(request, user_id):
    return render(
        request,
        'employee_360.html',
        {
            'target_user_id': user_id
        }
    )