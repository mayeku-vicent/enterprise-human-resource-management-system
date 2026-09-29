from django.contrib import admin

from .models import (
    Permission,
    Role,
    RolePermission,
    UserRole,
)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "module",
        "is_active",
    )

    list_filter = (
        "module",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "description",
        "module",
    )

    ordering = (
        "module",
        "code",
    )


class RolePermissionInline(admin.TabularInline):
    model = RolePermission
    extra = 1
    autocomplete_fields = ("permission",)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_system_role",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_system_role",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
        "description",
    )

    ordering = (
        "name",
    )

    inlines = (
        RolePermissionInline,
    )

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_system_role:
            return (
                "code",
                "is_system_role",
            )

        return ()


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = (
        "role",
        "permission",
        "granted_at",
    )

    list_filter = (
        "role",
        "permission",
    )

    search_fields = (
        "role__code",
        "role__name",
        "permission__code",
        "permission__name",
    )

    autocomplete_fields = (
        "role",
        "permission",
    )


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "is_active",
        "assigned_at",
    )

    list_filter = (
        "role",
        "is_active",
    )

    search_fields = (
        "user__username",
        "user__email",
        "role__code",
        "role__name",
    )

    autocomplete_fields = (
        "user",
        "role",
    )

    readonly_fields = (
        "assigned_at",
    )