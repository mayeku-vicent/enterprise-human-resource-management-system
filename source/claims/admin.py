from django.contrib import admin
from .models import ExpenseClaim

@admin.register(ExpenseClaim)
class ExpenseClaimAdmin(admin.ModelAdmin):
    list_display = ('employee', 'claim_type', 'amount', 'status', 'created_at')
    list_filter = ('status', 'claim_type')
    search_fields = ('employee__username', 'description')