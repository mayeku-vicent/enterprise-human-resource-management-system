from django.db import models
from django.conf import settings

class ClaimType(models.TextChoices):
    MEDICAL = 'MEDICAL', 'Medical Expenses'
    TRANSPORT = 'TRANSPORT', 'Travel & Transport'
    FUNERAL = 'FUNERAL', 'Funeral & Welfare Support'
    OTHER = 'OTHER', 'Other Operational Expenses'
class ExpenseClaim(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    claim_type = models.CharField(max_length=20, choices=ClaimType.choices, default=ClaimType.OTHER)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.employee.username} - {self.claim_type} ({self.amount}) [{self.status}]"