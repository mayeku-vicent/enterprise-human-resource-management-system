from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class TrainingCourse(models.Model):
    title = models.CharField(max_length=200)
    provider = models.CharField(max_length=150) # e.g. "Coursera", "Internal HR"
    description = models.TextField()
    duration_hours = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.provider})"

class EmployeeCertification(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certifications')
    certification_name = models.CharField(max_length=200)
    issuing_organization = models.CharField(max_length=150)
    issue_date = models.DateField()
    expiry_date = models.DateField(null=True, blank=True)
    credential_id = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.certification_name} - {self.employee.username}"