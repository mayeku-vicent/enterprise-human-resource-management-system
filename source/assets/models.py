from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CompanyAsset(models.Model):
    class AssetCategory(models.TextChoices):
        LAPTOP = 'LAPTOP', 'Laptop / Computer'
        PHONE = 'PHONE', 'Mobile Phone'
        VEHICLE = 'VEHICLE', 'Company Vehicle'
        ID_CARD = 'ID_CARD', 'Access / ID Card'
        EQUIPMENT = 'EQUIPMENT', 'Office Equipment'

    name = models.CharField(max_length=150)
    category = models.CharField(max_length=50, choices=AssetCategory.choices, default=AssetCategory.LAPTOP)
    serial_number = models.CharField(max_length=100, unique=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets')
    issue_date = models.DateField(null=True, blank=True)
    return_date = models.DateField(null=True, blank=True)
    condition = models.CharField(max_length=100, default='New / Good')

    def __str__(self):
        return f"{self.name} ({self.serial_number})"