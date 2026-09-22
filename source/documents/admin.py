from django.contrib import admin
from .models import EmployeeDocument

@admin.register(EmployeeDocument)
class EmployeeDocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'employee', 'category', 'uploaded_at', 'expiration_date')
    list_filter = ('category', 'uploaded_at')
    search_fields = ('title', 'employee__username')