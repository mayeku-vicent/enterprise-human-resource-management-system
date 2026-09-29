from rest_framework import permissions

from .services import (
    has_any_permission,
    has_permission,
    has_role,
)


class HasPermission(permissions.BasePermission):
    """
    Generic DRF permission class for one database-driven HRMS permission.

    Usage:
        permission_code = "employee.view"
    """

    permission_code = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        permission_code = getattr(
            view,
            "permission_code",
            self.permission_code,
        )

        if not permission_code:
            return False

        return has_permission(request.user, permission_code)


class HasAnyPermission(permissions.BasePermission):
    """
    Allows access when the authenticated user has at least one
    of the permissions declared by the view.

    Usage:
        permission_codes = [
            "employee.view",
            "employee.create",
        ]
    """

    permission_codes = ()

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        permission_codes = getattr(
            view,
            "permission_codes",
            self.permission_codes,
        )

        return has_any_permission(
            request.user,
            *permission_codes,
        )


class HasRole(permissions.BasePermission):
    """
    Generic DRF permission class for one database-driven HRMS role.

    Usage:
        role_code = "HR_ADMIN"
    """

    role_code = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        role_code = getattr(
            view,
            "role_code",
            self.role_code,
        )

        if not role_code:
            return False

        return has_role(request.user, role_code)


class IsAdmin(permissions.BasePermission):
    """
    Legacy compatibility permission.

    This remains available while existing HRMS code is migrated.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (
                request.user.is_superuser
                or has_role(request.user, "SYSTEM_ADMIN")
                or has_role(request.user, "SUPER_ADMIN")
            )
        )


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Legacy compatibility permission.

    Uses the new database-driven roles while the existing HRMS
    endpoints are migrated gradually.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return has_any_permission(
            request.user,
            "manager.access",
            "admin.access",
        ) or (
            has_role(request.user, "MANAGER")
            or has_role(request.user, "HR_ADMIN")
            or has_role(request.user, "SYSTEM_ADMIN")
            or has_role(request.user, "SUPER_ADMIN")
        )


class IsAuthenticatedEmployee(permissions.BasePermission):
    """
    Legacy compatibility permission.

    Any authenticated HRMS user with an active database role can pass.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user.user_roles.filter(
            is_active=True,
            role__is_active=True,
        ).exists()