from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeDocument(models.Model):
    class DocumentCategory(models.TextChoices):
        CONTRACT = 'CONTRACT', 'Employment Contract'
        ID_DOC = 'ID', 'Identification / Passport'
        CERTIFICATE = 'CERTIFICATE', 'Academic / Professional Certificate'
        TAX = 'TAX', 'Tax & Financial Document'
        OTHER = 'OTHER', 'Other Document'

    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=DocumentCategory.choices, default=DocumentCategory.OTHER)
    file = models.FileField(upload_to='employee_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.employee.username} ({self.category})"