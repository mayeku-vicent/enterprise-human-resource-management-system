from django.contrib import admin
from .models import TrainingCourse, EmployeeCertification

@admin.register(TrainingCourse)
class TrainingCourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'duration_hours', 'is_active')
    list_filter = ('is_active', 'provider')
    search_fields = ('title', 'provider')

@admin.register(EmployeeCertification)
class EmployeeCertificationAdmin(admin.ModelAdmin):
    list_display = ('certification_name', 'employee', 'issuing_organization', 'issue_date', 'expiry_date')
    list_filter = ('issuing_organization', 'issue_date')
    search_fields = ('certification_name', 'employee__username', 'credential_id')