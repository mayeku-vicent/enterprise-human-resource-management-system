from django.db import models
from django.conf import settings

class ExpenseClaim(models.Model):
    class ClaimType(models.TextChoices):
        MEDICAL = 'MEDICAL', 'Medical Expenses'
        TRAVEL = 'TRAVEL', 'Travel & Transport'
        FUNERAL = 'FUNERAL', 'Funeral & Welfare Support'
        OTHER = 'OTHER', 'Other Operational Expenses'

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending Review'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'

    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')
    claim_type = models.CharField(max_length=20, choices=ClaimType.choices, default=ClaimType.OTHER)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Claim amount in company currency")
    description = models.TextField(help_text="Detailed justification for the claim")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_claims')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.claim_type} (${self.amount}) [{self.status}]"