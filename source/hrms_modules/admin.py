from django.contrib import admin

from .models import Attendance, ExpenseClaim


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = ('employee', 'date', 'check_in_time', 'check_out_time', 'status')

    list_filter = ('status', 'date')

    search_fields = ('employee__username',)


@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):

    list_display = ('id', 'employee', 'claim_type', 'amount', 'status', 'created_at')

    list_filter = ('status', 'claim_type')

    search_fields = ('employee__username', 'claim_type', 'description')