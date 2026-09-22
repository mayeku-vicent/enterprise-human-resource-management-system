from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class PerformanceGoal(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.employee.username}"

class Appraisal(models.Model):
    class RatingChoices(models.TextChoices):
        EXCELLENT = 'EXCELLENT', 'Excellent (5/5)'
        GOOD = 'GOOD', 'Good (4/5)'
        SATISFACTORY = 'SATISFACTORY', 'Satisfactory (3/5)'
        NEEDS_IMPROVEMENT = 'NEEDS_IMPROVEMENT', 'Needs Improvement (2/5)'
        UNSATISFACTORY = 'UNSATISFACTORY', 'Unsatisfactory (1/5)'

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appraisals')
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='conducted_appraisals')
    review_period = models.CharField(max_length=50) # e.g. "Q2 2026 Review"
    rating = models.CharField(max_length=50, choices=RatingChoices.choices, default=RatingChoices.SATISFACTORY)
    comments = models.TextField()
    reviewed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appraisal for {self.employee.username} ({self.review_period})"