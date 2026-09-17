from django.db import models
from django.conf import settings

class LeaveRequest(models.Model):
    class LeaveType(models.TextChoices):
        ANNUAL = 'ANNUAL', 'Annual Leave'
        SICK = 'SICK', 'Sick Leave'
        MATERNITY = 'MATERNITY', 'Maternity Leave'
        UNPAID = 'UNPAID', 'Unpaid Leave'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices, default=LeaveType.ANNUAL)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_leaves')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.leave_type} ({self.status})"