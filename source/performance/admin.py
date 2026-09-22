from django.contrib import admin
from .models import PerformanceGoal, Appraisal

@admin.register(PerformanceGoal)
class PerformanceGoalAdmin(admin.ModelAdmin):
    list_display = ('title', 'employee', 'target_date', 'is_completed')
    list_filter = ('is_completed', 'target_date')
    search_fields = ('title', 'employee__username')

@admin.register(Appraisal)
class AppraisalAdmin(admin.ModelAdmin):
    list_display = ('employee', 'reviewer', 'review_period', 'rating', 'reviewed_at')
    list_filter = ('rating', 'review_period')
    search_fields = ('employee__username', 'reviewer__username')