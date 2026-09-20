from django.db import models
from django.conf import settings

class LeaveType(models.TextChoices):
    ANNUAL = 'ANNUAL', 'Annual Leave'
    SICK = 'SICK', 'Sick Leave'
    MATERNITY = 'MATERNITY', 'Maternity/Paternity Leave'
    STUDY = 'STUDY', 'Study Leave'
    OTHER = 'OTHER', 'Other Leave'

class LeaveRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    leave_type = models.CharField(max_length=20, choices=LeaveType.choices, default=LeaveType.ANNUAL)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.leave_type} ({self.status})"