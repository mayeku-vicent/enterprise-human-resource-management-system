from .models import UserRole


# ---------------------------------------------------------------------------
# LEGACY ROLE HELPERS
# ---------------------------------------------------------------------------
# These are kept for compatibility with the existing HRMS code.
# We will migrate existing views gradually to the new database-driven
# Role + Permission system instead of breaking everything at once.


def is_admin(user):
    return (
        user
        and user.is_authenticated
        and user.role == "ADMIN"
    )


def is_manager(user):
    return (
        user
        and user.is_authenticated
        and user.role == "MANAGER"
    )


def is_employee(user):
    return (
        user
        and user.is_authenticated
        and user.role == "EMPLOYEE"
    )


def is_manager_or_admin(user):
    return (
        user
        and user.is_authenticated
        and user.role in ["MANAGER", "ADMIN"]
    )


def is_owner(user, target_user):
    return (
        user
        and user.is_authenticated
        and target_user
        and user.pk == target_user.pk
    )


def is_manager_of(manager_user, employee_user):
    """
    Returns True if manager_user manages employee_user.
    """

    if not manager_user or not manager_user.is_authenticated:
        return False

    if manager_user.role != "MANAGER":
        return False

    if not employee_user:
        return False

    try:
        profile = employee_user.employee_profile
    except AttributeError:
        return False

    if not profile.manager:
        return False

    return profile.manager.user_id == manager_user.pk


def can_access_employee(user, target_user):
    if not user or not user.is_authenticated:
        return False

    if not target_user:
        return False

    if is_admin(user):
        return True

    if is_owner(user, target_user):
        return True

    if is_manager_of(user, target_user):
        return True

    return False


# ---------------------------------------------------------------------------
# DATABASE-DRIVEN ROLE + PERMISSION SYSTEM
# ---------------------------------------------------------------------------


def has_role(user, role_code):
    """
    Returns True when the authenticated user has an active HRMS role.

    Example:
        has_role(user, "HR_ADMIN")
        has_role(user, "PAYROLL_OFFICER")
    """

    if not user or not user.is_authenticated:
        return False

    # Django superusers retain unrestricted access.
    if user.is_superuser:
        return True

    return UserRole.objects.filter(
        user=user,
        role__code=role_code,
        role__is_active=True,
        is_active=True,
    ).exists()


def has_permission(user, permission_code):
    """
    Returns True when the authenticated user has an active role
    containing the requested active permission.

    Example:
        has_permission(user, "employee.view")
        has_permission(user, "employee.create")
    """

    if not user or not user.is_authenticated:
        return False

    # Django superusers retain unrestricted access.
    if user.is_superuser:
        return True

    return UserRole.objects.filter(
        user=user,
        role__is_active=True,
        is_active=True,
        role__permissions__code=permission_code,
        role__permissions__is_active=True,
    ).exists()


def has_any_permission(user, *permission_codes):
    """
    Returns True when the user has at least one of the supplied permissions.

    Example:
        has_any_permission(
            user,
            "employee.view",
            "employee.create",
        )
    """

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not permission_codes:
        return False

    return UserRole.objects.filter(
        user=user,
        role__is_active=True,
        is_active=True,
        role__permissions__code__in=permission_codes,
        role__permissions__is_active=True,
    ).exists()


def has_all_permissions(user, *permission_codes):
    """
    Returns True only when the user has every supplied permission.

    Example:
        has_all_permissions(
            user,
            "employee.view",
            "employee.edit",
        )
    """

    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    if not permission_codes:
        return True

    required_permissions = set(permission_codes)

    granted_permissions = set(
        UserRole.objects.filter(
            user=user,
            role__is_active=True,
            is_active=True,
            role__permissions__code__in=required_permissions,
            role__permissions__is_active=True,
        )
        .values_list("role__permissions__code", flat=True)
        .distinct()
    )

    return required_permissions.issubset(granted_permissions)