from django.db.models import Q

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import WorkShift, EmployeeShiftAssignment
from .serializers import (
    WorkShiftSerializer,
    EmployeeShiftAssignmentSerializer,
)

from accounts.models import EmployeeProfile


class WorkShiftViewSet(viewsets.ModelViewSet):
    """
    Secure Work Shift API.

    READ access:
    - ADMIN: all shifts.
    - MANAGER: all active/available shifts.
    - EMPLOYEE: all active/available shifts.

    WRITE access:
    - ADMIN: create, update, and delete shifts.
    - MANAGER: read-only.
    - EMPLOYEE: read-only.
    """

    serializer_class = WorkShiftSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return WorkShift.objects.all().order_by("name")

        return WorkShift.objects.all().order_by("name")

    def create(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to create work shifts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to update work shifts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to update work shifts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to delete work shifts."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return super().destroy(request, *args, **kwargs)


class EmployeeShiftAssignmentViewSet(viewsets.ModelViewSet):
    """
    Secure Employee Shift Assignment API.

    READ access:
    - ADMIN: all assignments.
    - MANAGER: own assignments and assignments of direct reports.
    - EMPLOYEE: own assignments only.

    WRITE access:
    - ADMIN: full management.
    - MANAGER: manage assignments for direct reports.
    - EMPLOYEE: manage their own assignments only.

    Employee ownership is always validated server-side.
    """

    serializer_class = EmployeeShiftAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return EmployeeShiftAssignment.objects.all().order_by(
                "-assigned_date"
            )

        if user.role == "MANAGER":
            return EmployeeShiftAssignment.objects.filter(
                Q(employee=user)
                | Q(
                    employee__employee_profile__manager__user=user
                )
            ).distinct().order_by("-assigned_date")

        return EmployeeShiftAssignment.objects.filter(
            employee=user
        ).order_by("-assigned_date")

    def create(self, request, *args, **kwargs):
        user = request.user

        employee_id = request.data.get("employee")

        if not employee_id:
            return Response(
                {"detail": "The employee field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            employee_id = int(employee_id)
        except (TypeError, ValueError):
            return Response(
                {
                    "detail": (
                        "The employee field must contain "
                        "a valid employee ID."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        from accounts.models import User

        target_employee = User.objects.filter(
            id=employee_id
        ).first()

        if target_employee is None:
            return Response(
                {"detail": "The specified employee does not exist."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user.role == "ADMIN":
            allowed = True

        elif user.role == "MANAGER":
            allowed = EmployeeProfile.objects.filter(
                user=target_employee,
                manager__user=user
            ).exists()

        else:
            allowed = target_employee == user

        if not allowed:
            return Response(
                {
                    "detail": (
                        "You are not authorized to create "
                        "a shift assignment for this employee."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(employee=target_employee)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        assignment = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        if user == assignment.employee:
            serializer = self.get_serializer(
                assignment,
                data=request.data,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(employee=assignment.employee)

            return Response(serializer.data)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=assignment.employee,
                manager__user=user,
            ).exists()

            if is_direct_report:
                serializer = self.get_serializer(
                    assignment,
                    data=request.data,
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(employee=assignment.employee)

                return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "You are not authorized to update "
                    "this shift assignment."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    def partial_update(self, request, *args, **kwargs):
        assignment = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().partial_update(request, *args, **kwargs)

        if user == assignment.employee:
            serializer = self.get_serializer(
                assignment,
                data=request.data,
                partial=True,
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(employee=assignment.employee)

            return Response(serializer.data)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=assignment.employee,
                manager__user=user,
            ).exists()

            if is_direct_report:
                serializer = self.get_serializer(
                    assignment,
                    data=request.data,
                    partial=True,
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(employee=assignment.employee)

                return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "You are not authorized to update "
                    "this shift assignment."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    def destroy(self, request, *args, **kwargs):
        assignment = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().destroy(request, *args, **kwargs)

        if user == assignment.employee:
            return super().destroy(request, *args, **kwargs)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=assignment.employee,
                manager__user=user,
            ).exists()

            if is_direct_report:
                return super().destroy(request, *args, **kwargs)

        return Response(
            {
                "detail": (
                    "You are not authorized to delete "
                    "this shift assignment."
                )
            },
            status=status.HTTP_403_FORBIDDEN,
        )