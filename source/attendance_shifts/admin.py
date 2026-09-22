from django.contrib import admin
from .models import WorkShift, EmployeeShiftAssignment

@admin.register(WorkShift)
class WorkShiftAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time', 'grace_period_minutes')
    search_fields = ('name',)

@admin.register(EmployeeShiftAssignment)
class EmployeeShiftAssignmentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'shift', 'assigned_date')
    list_filter = ('assigned_date', 'shift')
    search_fields = ('employee__username',)