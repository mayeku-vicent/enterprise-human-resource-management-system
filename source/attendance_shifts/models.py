from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WorkShift(models.Model):
    name = models.CharField(max_length=100) # e.g. "Morning Shift (8AM - 5PM)"
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_period_minutes = models.PositiveIntegerField(default=15)

    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class EmployeeShiftAssignment(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shift_assignments')
    shift = models.ForeignKey(WorkShift, on_delete=models.CASCADE)
    assigned_date = models.DateField()

    def __str__(self):
        return f"{self.employee.username} assigned to {self.shift.name} on {self.assigned_date}"