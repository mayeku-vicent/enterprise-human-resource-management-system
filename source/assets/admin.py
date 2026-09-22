from django.contrib import admin
from .models import CompanyAsset

@admin.register(CompanyAsset)
class CompanyAssetAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'serial_number', 'assigned_to', 'issue_date', 'condition')
    list_filter = ('category', 'condition')
    search_fields = ('name', 'serial_number')