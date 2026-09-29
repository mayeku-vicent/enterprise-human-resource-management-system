from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from compliance.models import AuditLog
from django.db.models import Q

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
from config.security import get_client_ip

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
    """
    Secure Employee Profile API.

    READ access:
    - ADMIN: all employee profiles.
    - MANAGER: own profile and direct reports.
    - EMPLOYEE: own profile only.

    WRITE access:
    - ADMIN: can create, update and delete profiles.
    - EMPLOYEE: can update their own profile.
    - MANAGER: cannot modify employee profiles.
    """

    serializer_class = EmployeeProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------
        if user.role == "ADMIN":
            return EmployeeProfile.objects.all().order_by(
                "user__username"
            )

        # ----------------------------------------------------
        # MANAGER
        # Own profile + direct reports
        # ----------------------------------------------------
        if user.role == "MANAGER":
            return EmployeeProfile.objects.filter(
                Q(user=user)
                | Q(manager__user=user)
            ).distinct().order_by(
                "user__username"
            )

        # ----------------------------------------------------
        # EMPLOYEE
        # Own profile only
        # ----------------------------------------------------
        return EmployeeProfile.objects.filter(
            user=user
        ).order_by(
            "user__username"
        )

    def create(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to create employee profiles."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        profile = self.get_object()

        if request.user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        if request.user != profile.user:
            return Response(
                {
                    "detail": (
                        "You can only update your own "
                        "employee profile."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to delete employee profiles."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

# ============================================================
# ATTENDANCE API
# ============================================================

class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.all().order_by('-date')
    serializer_class = AttendanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Attendance.objects.all().order_by('-date')

        if user.role == "MANAGER":
            return Attendance.objects.filter(
                employee__employee_profile__manager__user=user
            ).order_by('-date')

        return Attendance.objects.filter(
            employee=user
        ).order_by('-date')

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def update(self, request, *args, **kwargs):
        attendance = self.get_object()

        if request.user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        if request.user.role == "MANAGER":
            manager_user = getattr(
                getattr(getattr(attendance.employee, 'employee_profile', None), 'manager', None),
                'user',
                None
            )
            if manager_user != request.user:
                return Response(
                    {"detail": "You can only update attendance records for your direct reports."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return super().update(request, *args, **kwargs)

        if attendance.employee != request.user:
            return Response(
                {"detail": "You can only update your own attendance records."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        attendance = self.get_object()

        if request.user.role == "ADMIN":
            return super().destroy(request, *args, **kwargs)

        return Response(
            {"detail": "Only Administrators are authorized to delete attendance records."},
            status=status.HTTP_403_FORBIDDEN
        )


# ============================================================
# EXPENSE CLAIM API
# ============================================================

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all().order_by('-created_at')
    serializer_class = ExpenseClaimSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return ExpenseClaim.objects.all().order_by('-created_at')

        if user.role == "MANAGER":
            return ExpenseClaim.objects.filter(
                employee__employee_profile__manager__user=user
            ).order_by('-created_at')

        return ExpenseClaim.objects.filter(
            employee=user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

    def update(self, request, *args, **kwargs):
        claim = self.get_object()

        if request.user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        if request.user.role == "MANAGER":
            manager_user = getattr(
                getattr(getattr(claim.employee, 'employee_profile', None), 'manager', None),
                'user',
                None
            )
            if manager_user != request.user:
                return Response(
                    {"detail": "You can only update claims for your direct reports."},
                    status=status.HTTP_403_FORBIDDEN
                )
            return super().update(request, *args, **kwargs)

        if claim.employee != request.user:
            return Response(
                {"detail": "You can only update your own claims."},
                status=status.HTTP_403_FORBIDDEN
            )

        if claim.status != ExpenseClaim.Status.PENDING:
            return Response(
                {"detail": "Only pending claims can be updated."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        claim = self.get_object()

        if request.user.role == "ADMIN":
            return super().destroy(request, *args, **kwargs)

        if claim.employee != request.user:
            return Response(
                {"detail": "You can only delete your own claims."},
                status=status.HTTP_403_FORBIDDEN
            )

        if claim.status != ExpenseClaim.Status.PENDING:
            return Response(
                {"detail": "Only pending claims can be deleted."},
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        claim = self.get_object()

        if request.user.role == "EMPLOYEE":
            return Response(
                {"detail": "Employees are not authorized to approve claims."},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user.role == "MANAGER":
            manager_user = getattr(
                getattr(getattr(claim.employee, 'employee_profile', None), 'manager', None),
                'user',
                None
            )
            if manager_user != request.user:
                return Response(
                    {"detail": "You can only approve claims for your direct reports."},
                    status=status.HTTP_403_FORBIDDEN
                )

        claim.status = ExpenseClaim.Status.APPROVED
        claim.save()

        return Response(
            {'status': 'Claim Approved'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['patch'])
    def mark_paid(self, request, pk=None):
        if request.user.role != "ADMIN":
            return Response(
                {"detail": "Only Administrators can mark claims as paid."},
                status=status.HTTP_403_FORBIDDEN
            )

        claim = self.get_object()

        claim.status = ExpenseClaim.Status.PAID
        claim.save()

        return Response(
            {'status': 'Claim Marked as Paid'},
            status=status.HTTP_200_OK
        )

# ============================================================
# LEAVE REQUEST API
# ============================================================

class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all().order_by('-created_at')
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------
        if user.role == "ADMIN":
            return LeaveRequest.objects.all().order_by('-created_at')

        # ----------------------------------------------------
        # MANAGER
        # Only leave requests belonging to direct reports
        # ----------------------------------------------------
        if user.role == "MANAGER":
            return LeaveRequest.objects.filter(
                employee__employee_profile__manager__user=user
            ).order_by('-created_at')

        # ----------------------------------------------------
        # EMPLOYEE
        # Only own leave requests
        # ----------------------------------------------------
        return LeaveRequest.objects.filter(
            employee=user
        ).order_by('-created_at')

    def perform_create(self, serializer):
        # Always assign the authenticated user as the employee.
        # The employee field cannot be supplied by another user.
        serializer.save(employee=self.request.user)

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(self, request, *args, **kwargs):
        leave_request = self.get_object()

        # ADMIN can update any leave request
        if request.user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        # MANAGER can update requests belonging to direct reports
        if request.user.role == "MANAGER":
            manager_user = getattr(
                getattr(
                    getattr(
                        leave_request.employee,
                        'employee_profile',
                        None
                    ),
                    'manager',
                    None
                ),
                'user',
                None
            )

            if manager_user != request.user:
                return Response(
                    {
                        "detail": (
                            "You can only update leave requests "
                            "for your direct reports."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            return super().update(request, *args, **kwargs)

        # EMPLOYEE can only update own requests
        if leave_request.employee != request.user:
            return Response(
                {
                    "detail": (
                        "You can only update your own "
                        "leave requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Employees can only update pending requests
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending leave requests "
                        "can be updated."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    # --------------------------------------------------------
    # PARTIAL UPDATE / PATCH
    # --------------------------------------------------------

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def destroy(self, request, *args, **kwargs):
        leave_request = self.get_object()

        # ADMIN can delete any leave request
        if request.user.role == "ADMIN":
            return super().destroy(request, *args, **kwargs)

        # Everyone else can only delete their own request
        if leave_request.employee != request.user:
            return Response(
                {
                    "detail": (
                        "You can only delete your own "
                        "leave requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # Employees can only delete pending requests
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending leave requests "
                        "can be deleted."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

    # --------------------------------------------------------
    # APPROVE
    # --------------------------------------------------------

    @action(detail=True, methods=['patch'])
    def approve(self, request, pk=None):
        leave_request = self.get_object()

        # EMPLOYEES CANNOT APPROVE
        if request.user.role == "EMPLOYEE":
            return Response(
                {
                    "detail": (
                        "Employees are not authorized "
                        "to approve leave requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # MANAGER can approve only direct reports
        if request.user.role == "MANAGER":
            manager_user = getattr(
                getattr(
                    getattr(
                        leave_request.employee,
                        'employee_profile',
                        None
                    ),
                    'manager',
                    None
                ),
                'user',
                None
            )

            if manager_user != request.user:
                return Response(
                    {
                        "detail": (
                            "You can only approve leave requests "
                            "for your direct reports."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # Only pending requests should be approved
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending leave requests "
                        "can be approved."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.status = LeaveRequest.Status.APPROVED
        leave_request.save(
            update_fields=['status']
        )

        return Response(
            {
                "status": "Leave Request Approved"
            },
            status=status.HTTP_200_OK
        )

    # --------------------------------------------------------
    # REJECT
    # --------------------------------------------------------

    @action(detail=True, methods=['patch'])
    def reject(self, request, pk=None):
        leave_request = self.get_object()

        # EMPLOYEES CANNOT REJECT
        if request.user.role == "EMPLOYEE":
            return Response(
                {
                    "detail": (
                        "Employees are not authorized "
                        "to reject leave requests."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        # MANAGER can reject only direct reports
        if request.user.role == "MANAGER":
            manager_user = getattr(
                getattr(
                    getattr(
                        leave_request.employee,
                        'employee_profile',
                        None
                    ),
                    'manager',
                    None
                ),
                'user',
                None
            )

            if manager_user != request.user:
                return Response(
                    {
                        "detail": (
                            "You can only reject leave requests "
                            "for your direct reports."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

        # Only pending requests should be rejected
        if leave_request.status != LeaveRequest.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending leave requests "
                        "can be rejected."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        leave_request.status = LeaveRequest.Status.REJECTED
        leave_request.save(
            update_fields=['status']
        )

        return Response(
            {
                "status": "Leave Request Rejected"
            },
            status=status.HTTP_200_OK
        )

# ============================================================
# PAYROLL API
# ============================================================

class PayrollViewSet(viewsets.ModelViewSet):
    """
    Payroll API backed by the actual Payslip model.

    Access rules:
    - ADMIN: can view, create, update and delete all payslips.
    - MANAGER: can view payslips belonging to direct reports.
    - EMPLOYEE: can view only their own payslips.
    - Only ADMIN can create, modify or delete payslips.
    """

    serializer_class = PayslipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------
        if user.role == "ADMIN":
            return Payslip.objects.all().order_by("-generated_at")

        # ----------------------------------------------------
        # MANAGER
        # ----------------------------------------------------
        if user.role == "MANAGER":
            return Payslip.objects.filter(
                employee__employee_profile__manager__user=user
            ).order_by("-generated_at")

        # ----------------------------------------------------
        # EMPLOYEE
        # ----------------------------------------------------
        return Payslip.objects.filter(
            employee=user
        ).order_by("-generated_at")

    # --------------------------------------------------------
    # CREATE
    # --------------------------------------------------------

    def create(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to create payroll records."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    # --------------------------------------------------------
    # UPDATE
    # --------------------------------------------------------

    def update(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to modify payroll records."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    # --------------------------------------------------------
    # PARTIAL UPDATE / PATCH
    # --------------------------------------------------------

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    # --------------------------------------------------------
    # DELETE
    # --------------------------------------------------------

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to delete payroll records."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)

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
        # ----------------------------------------------------
        # EMPLOYEE 360 AUTHORIZATION
        # ----------------------------------------------------

        user = request.user

        if user.role == "ADMIN":
            allowed = True

        elif user.role == "MANAGER":
            allowed = (
                target_user == user
                or EmployeeProfile.objects.filter(
                    user=target_user,
                    manager__user=user
                ).exists()
            )

        else:
            allowed = target_user == user

        if not allowed:
            return Response(
                {
                    "detail": (
                        "You are not authorized to access "
                        "this employee's records."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )
        # ----------------------------------------------------
        # EMPLOYEE 360 SENSITIVE DATA AUTHORIZATION
        # ----------------------------------------------------
        #
        # Managers may access the employee's general HR data,
        # but compensation, payroll, audit history and
        # emergency-contact information are restricted.
        #
        # Employees can access their own complete record.
        # Administrators can access all records.
        # ----------------------------------------------------

        sensitive_data_allowed = (
            user.role == "ADMIN"
            or target_user == user
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
        # COMPENSATION / SALARY & PAYROLL
        # ----------------------------------------------------

                # ----------------------------------------------------
        # COMPENSATION / SALARY & PAYROLL
        # ----------------------------------------------------

        if sensitive_data_allowed:
            salary = EmployeeSalary.objects.filter(
                employee=target_user
            ).first()

            payslips = Payslip.objects.filter(
                employee=target_user
            ).order_by('-generated_at')

        else:
            salary = None
            payslips = Payslip.objects.none()
        # ----------------------------------------------------
        # DOCUMENTS
        # ----------------------------------------------------

        documents = EmployeeDocument.objects.filter(
            employee=target_user
        ).order_by('-uploaded_at')

        # ----------------------------------------------------
        # AUDIT HISTORY
        # ----------------------------------------------------
        if sensitive_data_allowed:
            audit_history = AuditLog.objects.filter(
                user=target_user
            ).order_by('-timestamp')
        else:
            audit_history = AuditLog.objects.none()

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
            ).order_by(
                '-is_primary',
                'id'
            )
            if profile and sensitive_data_allowed
            else EmployeeContact.objects.none()
        )

        # ----------------------------------------------------
        # EMERGENCY CONTACTS
        # ----------------------------------------------------

        emergency_contacts = (
            EmergencyContact.objects.filter(
                employee=profile
            ).order_by(
                '-is_primary',
                'id'
            )
            if profile and sensitive_data_allowed
            else EmergencyContact.objects.none()
        )

             # ----------------------------------------------------
        # EMPLOYEE 360 PROFILE PRIVACY
        # ----------------------------------------------------

        profile_data = (
            EmployeeProfileSerializer(profile).data
            if profile
            else None
        )

        if (
            profile_data is not None
            and user.role == "MANAGER"
            and target_user != user
        ):
            profile_data.pop("phone_number", None)
            profile_data.pop("emergency_contact", None)
            profile_data.pop("location", None)

            if isinstance(profile_data.get("user"), dict):
                profile_data["user"].pop("email", None)


        # ----------------------------------------------------
        # EMPLOYEE 360 RESPONSE
        # ----------------------------------------------------

        data = {
            "user_id": target_user.id,
            "username": target_user.username,
            "email": (
                None
                if user.role == "MANAGER" and target_user != user
                else target_user.email
            ),
            "first_name": target_user.first_name,
            "last_name": target_user.last_name,
            "profile": profile_data,

            "profile": (
                EmployeeProfileSerializer(profile).data
                if profile
                else None
            ),

            "attendance_history": AttendanceSerializer(
                attendances,
                many=True
            ).data,

            "expense_claims": ExpenseClaimSerializer(
                claims,
                many=True
            ).data,

            "leave_requests": LeaveRequestSerializer(
                leaves,
                many=True
            ).data,

            "assets": CompanyAssetSerializer(
                assets,
                many=True
            ).data,

            "performance_goals": PerformanceGoalSerializer(
                goals,
                many=True
            ).data,

            "appraisals": AppraisalSerializer(
                appraisals,
                many=True
            ).data,

            "certifications": EmployeeCertificationSerializer(
                certifications,
                many=True
            ).data,

            "shift_assignments": EmployeeShiftAssignmentSerializer(
                shifts,
                many=True
            ).data,

            "salary": (
                EmployeeSalarySerializer(salary).data
                if salary
                else None
            ),

            "payslips": PayslipSerializer(
                payslips,
                many=True
            ).data,

            "documents": EmployeeDocumentSerializer(
                documents,
                many=True
            ).data,

            "audit_history": AuditLogSerializer(
                audit_history,
                many=True
            ).data,

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
# SECURE EMPLOYEE DOCUMENT VIEW
# ============================================================

@login_required
def secure_employee_document_view(request, document_id):
    """
    Securely serves employee documents.

    Access rules:
    - ADMIN: can view any employee document.
    - MANAGER: can view documents belonging to direct reports.
    - EMPLOYEE: can view only their own documents.

    Every access attempt is recorded in AuditLog.
    """

    document = get_object_or_404(
        EmployeeDocument,
        id=document_id
    )

    user = request.user

    # --------------------------------------------------------
    # GET CLIENT IP
    # --------------------------------------------------------

    ip_address = get_client_ip(request)

    # --------------------------------------------------------
    # AUTHORIZATION
    # --------------------------------------------------------

    if user.role == "ADMIN":
        allowed = True

    elif user.role == "MANAGER":
        allowed = EmployeeProfile.objects.filter(
            user=document.employee,
            manager__user=user
        ).exists()

    else:
        allowed = document.employee == user

    # --------------------------------------------------------
    # AUDIT ACCESS ATTEMPT
    # --------------------------------------------------------

    AuditLog.objects.create(
        user=user,
        action="DOCUMENT_ACCESS",
        ip_address=ip_address,
        description=(
            f"Employee document access attempt. "
            f"Document ID: {document.id}. "
            f"Document owner: {document.employee.username}. "
            f"Result: {'ALLOWED' if allowed else 'DENIED'}."
        )
    )

    # --------------------------------------------------------
    # DENY UNAUTHORIZED ACCESS
    # --------------------------------------------------------

    if not allowed:
        from django.http import JsonResponse

        return JsonResponse(
            {
                "detail": (
                    "You are not authorized to access "
                    "this employee document."
                )
            },
            status=403
        )

    # --------------------------------------------------------
    # CHECK FILE EXISTS
    # --------------------------------------------------------

    if not document.file:
        AuditLog.objects.create(
            user=user,
            action="DOCUMENT_ACCESS_ERROR",
            ip_address=ip_address,
            description=(
                f"Employee document access failed because "
                f"Document ID {document.id} contains no file."
            )
        )

        from django.http import JsonResponse

        return JsonResponse(
            {
                "detail": "This document does not contain a file."
            },
            status=404
        )

    # --------------------------------------------------------
    # SERVE FILE SECURELY
    # --------------------------------------------------------

    from django.http import FileResponse

    return FileResponse(
        document.file.open("rb"),
        as_attachment=False,
        filename=document.file.name.split("/")[-1]
    )

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


@login_required
def attendance_dashboard_view(request):
    return render(
        request,
        'attendance_dashboard.html'
    )


@login_required
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
@login_required
def employee_360_view(request, user_id):
    """
    Secure Employee 360 UI access.

    Access rules:
    - ADMIN: can view any employee.
    - MANAGER: can view themselves and their direct reports.
    - EMPLOYEE: can view only themselves.
    """

    target_user = get_object_or_404(
        User,
        id=user_id
    )

    user = request.user

    # ----------------------------------------------------
    # EMPLOYEE 360 UI AUTHORIZATION
    # ----------------------------------------------------

    if user.role == "ADMIN":
        allowed = True

    elif user.role == "MANAGER":
        allowed = (
            target_user == user
            or EmployeeProfile.objects.filter(
                user=target_user,
                manager__user=user
            ).exists()
        )

    else:
        allowed = target_user == user

    if not allowed:
        return JsonResponse(
            {
                "detail": (
                    "You are not authorized to access "
                    "this employee's records."
                )
            },
            status=403
        )

    return render(
        request,
        'employee_360.html',
        {
            'target_user_id': user_id
        }
    )

