from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmployeeProfile

class EmployeeProfileInline(admin.StackedInline):
    model = EmployeeProfile
    can_delete = False
    verbose_name_plural = 'Employee Profile'

class CustomUserAdmin(UserAdmin):
    model = User
    inlines = (EmployeeProfileInline,)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    
    list_filter = ('role', 'is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Enterprise Role Info', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Enterprise Role Info', {'fields': ('role',)}),
    )

admin.site.register(User, CustomUserAdmin)