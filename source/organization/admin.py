from django.contrib import admin
from .models import Department, Position

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'created_at')
    search_fields = ('name', 'code')

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'grade')
    list_filter = ('department', 'grade')
    search_fields = ('title', 'department__name')