from django.conf import settings
from django.db import models


class Permission(models.Model):
    """
    A single action that a user may be allowed to perform.
    """

    code = models.CharField(
        max_length=100,
        unique=True,
        help_text="Unique permission code, e.g. employee.view",
    )
    name = models.CharField(
        max_length=150,
        help_text="Human-readable permission name.",
    )
    description = models.TextField(
        blank=True,
        help_text="What this permission allows the user to do.",
    )
    module = models.CharField(
        max_length=100,
        blank=True,
        help_text="HRMS module this permission belongs to.",
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["module", "code"]

    def __str__(self):
        return self.code


class Role(models.Model):
    """
    A collection of permissions assigned to users.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique role code, e.g. HR_ADMIN.",
    )
    name = models.CharField(
        max_length=100,
        unique=True,
    )
    description = models.TextField(blank=True)

    is_system_role = models.BooleanField(
        default=False,
        help_text="System roles are protected from accidental deletion.",
    )
    is_active = models.BooleanField(default=True)

    permissions = models.ManyToManyField(
        Permission,
        through="RolePermission",
        related_name="roles",
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    """
    Connects a Role to a Permission.
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name="role_permissions",
    )
    granted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["role", "permission"],
                name="unique_role_permission",
            )
        ]

    def __str__(self):
        return f"{self.role.code} -> {self.permission.code}"


class UserRole(models.Model):
    """
    Connects an accounts.User to a Role.

    This allows one user to have multiple roles while keeping
    the existing User.role field temporarily for compatibility.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "role"],
                name="unique_user_role",
            )
        ]
        ordering = ["-assigned_at"]

    def __str__(self):
        return f"{self.user.username} -> {self.role.name}"