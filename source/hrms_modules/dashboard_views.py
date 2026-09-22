from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.utils import timezone

from accounts.models import EmployeeProfile
from attendance_shifts.models import EmployeeShiftAssignment
from hrms_modules.models import Attendance
from leave.models import LeaveRequest
from recruitment.models import JobVacancy, Applicant
from payroll.models import Payslip
from performance.models import Appraisal


@login_required
def central_dashboard_view(request):
    today = timezone.localdate()
    current_month_start = today.replace(day=1)

    # ---------------------------------------------------------
    # EMPLOYEE KPIs
    # ---------------------------------------------------------
    total_employees = EmployeeProfile.objects.count()

    active_employees = EmployeeProfile.objects.filter(
        user__is_active=True
    ).count()

    new_employees = EmployeeProfile.objects.filter(
        date_of_joining__gte=current_month_start,
        date_of_joining__lte=today,
    ).count()

    # ---------------------------------------------------------
    # ATTENDANCE KPIs
    # ---------------------------------------------------------
    employees_absent = Attendance.objects.filter(
        date=today,
        status=Attendance.Status.ABSENT,
    ).count()

    employees_present = Attendance.objects.filter(
        date=today,
        status=Attendance.Status.PRESENT,
    ).count()

    employees_late = Attendance.objects.filter(
        date=today,
        status=Attendance.Status.LATE,
    ).count()

    # ---------------------------------------------------------
    # LEAVE KPIs
    # ---------------------------------------------------------
    employees_on_leave = LeaveRequest.objects.filter(
        status=LeaveRequest.Status.APPROVED,
        start_date__lte=today,
        end_date__gte=today,
    ).count()

    pending_leave_approvals = LeaveRequest.objects.filter(
        status=LeaveRequest.Status.PENDING
    ).count()

    # ---------------------------------------------------------
    # RECRUITMENT
    # ---------------------------------------------------------
    open_vacancies = JobVacancy.objects.filter(
        is_active=True
    ).count()

    applicant_pipeline = list(
        Applicant.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    # ---------------------------------------------------------
    # PAYROLL
    # ---------------------------------------------------------
    latest_payslip = Payslip.objects.order_by(
        '-generated_at'
    ).first()

    latest_payroll_amount = 0

    if latest_payslip:
        latest_payroll_period = latest_payslip.pay_period

        latest_payroll_amount = (
            Payslip.objects.filter(
                pay_period=latest_payroll_period
            ).aggregate(
                total=Sum('net_pay')
            )['total'] or 0
        )
    else:
        latest_payroll_period = None

    # ---------------------------------------------------------
    # PERFORMANCE
    # ---------------------------------------------------------
    performance_distribution = list(
        Appraisal.objects.values('rating')
        .annotate(total=Count('id'))
        .order_by('rating')
    )

    # ---------------------------------------------------------
    # DEPARTMENT HEADCOUNT
    # ---------------------------------------------------------
    department_headcount = list(
        EmployeeProfile.objects
        .filter(department__isnull=False)
        .values('department__name')
        .annotate(total=Count('id'))
        .order_by('-total', 'department__name')
    )

    # ---------------------------------------------------------
    # CENTRAL APPROVAL COUNT
    # ---------------------------------------------------------
    pending_approvals = pending_leave_approvals

    context = {
        'today': today,

        # Employee KPIs
        'total_employees': total_employees,
        'active_employees': active_employees,
        'new_employees': new_employees,

        # Attendance KPIs
        'employees_absent': employees_absent,
        'employees_present': employees_present,
        'employees_late': employees_late,

        # Leave KPIs
        'employees_on_leave': employees_on_leave,

        # Recruitment
        'open_vacancies': open_vacancies,
        'applicant_pipeline': applicant_pipeline,

        # Approvals
        'pending_approvals': pending_approvals,

        # Payroll
        'latest_payroll_amount': latest_payroll_amount,
        'latest_payroll_period': latest_payroll_period,

        # Analytics
        'department_headcount': department_headcount,
        'performance_distribution': performance_distribution,
    }

    return render(
        request,
        'hrms_dashboard.html',
        context
    )
