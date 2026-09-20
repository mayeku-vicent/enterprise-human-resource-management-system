from django.contrib import admin
from .models import EmployeeProfile, Attendance, ExpenseClaim

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'department', 'job_title', 'phone_number', 'date_joined')
    search_fields = ('user__username', 'job_title', 'department')
    list_filter = ('department',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('employee__username',)
    
@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'claim_type', 'amount', 'status', 'created_at')  # Changed 'title' to 'claim_type'
    list_filter = ('status', 'claim_type')
    search_fields = ('employee__username', 'claim_type', 'description')