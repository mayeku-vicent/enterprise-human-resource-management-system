from django.db import models
from django.conf import settings
class EmployeeProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hrms_profile')
    department = models.ForeignKey('organization.Department', on_delete=models.SET_NULL, null=True, blank=True, related_name='hrms_employees')
    position = models.ForeignKey('organization.Position', on_delete=models.SET_NULL, null=True, blank=True, related_name='hrms_employees')
    job_title = models.CharField(max_length=100, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)

    def __str__(self):
        pos_name = self.position.title if self.position else (self.job_title or "Staff")
        dept_name = self.department.name if self.department else "Unassigned"
        return f"{self.user.get_full_name() or self.user.username} - {pos_name} ({dept_name})"

class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = 'PRESENT', 'Present'
        ABSENT = 'ABSENT', 'Absent'
        LATE = 'LATE', 'Late'

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField(auto_now_add=True)
    check_in_time = models.TimeField(auto_now_add=True)
    check_out_time = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PRESENT)

    class Meta:
        unique_together = ('employee', 'date')

    def __str__(self):
        return f"{self.employee.username} - {self.date} ({self.status})"


# 3. Expense Claims Module
class ExpenseClaim(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        PAID = 'PAID', 'Paid'

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='expense_claims')
    claim_type = models.CharField(max_length=150, default="General Expense")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.claim_type} ({self.amount})"