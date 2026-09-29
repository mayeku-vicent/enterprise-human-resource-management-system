from django.contrib.auth import get_user_model
from django.test import TestCase

from .models import Permission, Role, RolePermission, UserRole
from .services import (
    has_all_permissions,
    has_any_permission,
    has_permission,
    has_role,
)


User = get_user_model()


class AuthorizationServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="employee_test",
            password="TestPassword123!",
        )

        self.superuser = User.objects.create_superuser(
            username="superuser_test",
            password="TestPassword123!",
        )

        self.role = Role.objects.create(
            code="HR_ADMIN",
            name="HR Administrator",
            description="HR administration role.",
            is_system_role=True,
        )

        self.view_permission = Permission.objects.create(
            code="employee.view",
            name="View Employees",
            description="Allows viewing employees.",
            module="Core HR",
        )

        self.create_permission = Permission.objects.create(
            code="employee.create",
            name="Create Employee",
            description="Allows creating employees.",
            module="Core HR",
        )

        RolePermission.objects.create(
            role=self.role,
            permission=self.view_permission,
        )

        RolePermission.objects.create(
            role=self.role,
            permission=self.create_permission,
        )

    def test_user_without_role_is_denied(self):
        self.assertFalse(
            has_role(self.user, "HR_ADMIN")
        )

    def test_user_with_active_role_is_allowed(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertTrue(
            has_role(self.user, "HR_ADMIN")
        )

    def test_inactive_user_role_is_denied(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=False,
        )

        self.assertFalse(
            has_role(self.user, "HR_ADMIN")
        )

    def test_inactive_role_is_denied(self):
        self.role.is_active = False
        self.role.save()

        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertFalse(
            has_role(self.user, "HR_ADMIN")
        )

    def test_superuser_has_role_access(self):
        self.assertTrue(
            has_role(self.superuser, "ANY_ROLE")
        )

    def test_user_with_permission_is_allowed(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertTrue(
            has_permission(
                self.user,
                "employee.view",
            )
        )

    def test_user_without_permission_is_denied(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertFalse(
            has_permission(
                self.user,
                "employee.edit",
            )
        )

    def test_inactive_permission_is_denied(self):
        self.view_permission.is_active = False
        self.view_permission.save()

        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertFalse(
            has_permission(
                self.user,
                "employee.view",
            )
        )

    def test_superuser_has_any_permission(self):
        self.assertTrue(
            has_permission(
                self.superuser,
                "anything.at.all",
            )
        )

    def test_has_any_permission(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertTrue(
            has_any_permission(
                self.user,
                "employee.edit",
                "employee.view",
            )
        )

    def test_has_any_permission_returns_false_when_none_exist(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertFalse(
            has_any_permission(
                self.user,
                "employee.edit",
                "employee.delete",
            )
        )

    def test_has_all_permissions(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertTrue(
            has_all_permissions(
                self.user,
                "employee.view",
                "employee.create",
            )
        )

    def test_has_all_permissions_returns_false_when_missing(self):
        UserRole.objects.create(
            user=self.user,
            role=self.role,
            is_active=True,
        )

        self.assertFalse(
            has_all_permissions(
                self.user,
                "employee.view",
                "employee.create",
                "employee.edit",
            )
        )

    def test_superuser_has_all_permissions(self):
        self.assertTrue(
            has_all_permissions(
                self.superuser,
                "permission.one",
                "permission.two",
                "permission.three",
            )
        )