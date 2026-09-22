from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class JobVacancy(models.Model):
    title = models.CharField(max_length=200)
    department_name = models.CharField(max_length=100)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Applicant(models.Model):
    vacancy = models.ForeignKey(JobVacancy, on_delete=models.CASCADE, related_name='applicants')
    full_name = models.CharField(max_length=150)
    email = models.EmailField()
    status = models.CharField(max_length=50, default='APPLIED') # APPLIED, SHORTLISTED, HIRED
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name