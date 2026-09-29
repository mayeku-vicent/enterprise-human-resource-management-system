from django.db.models import Q

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import PerformanceGoal, Appraisal
from .serializers import PerformanceGoalSerializer, AppraisalSerializer

from accounts.models import EmployeeProfile


class PerformanceGoalViewSet(viewsets.ModelViewSet):
    """
    Secure Performance Goal API.

    READ access:
    - ADMIN: all performance goals.
    - MANAGER: own goals and goals belonging to direct reports.
    - EMPLOYEE: own goals only.

    WRITE access:
    - ADMIN: can manage all goals.
    - MANAGER: can manage own goals and goals of direct reports.
    - EMPLOYEE: can manage own goals only.

    Ownership is always validated server-side.
    """

    serializer_class = PerformanceGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return PerformanceGoal.objects.all().order_by(
                "-created_at"
            )

        if user.role == "MANAGER":
            return PerformanceGoal.objects.filter(
                Q(employee=user)
                | Q(
                    employee__employee_profile__manager__user=user
                )
            ).distinct().order_by(
                "-created_at"
            )

        return PerformanceGoal.objects.filter(
            employee=user
        ).order_by(
            "-created_at"
        )

    def create(self, request, *args, **kwargs):
        user = request.user

        employee_id = request.data.get("employee")

        if not employee_id:
            return Response(
                {
                    "detail": (
                        "The employee field is required."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
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
                status=status.HTTP_400_BAD_REQUEST
            )

        from accounts.models import User

        target_employee = User.objects.filter(
            id=employee_id
        ).first()

        if target_employee is None:
            return Response(
                {
                    "detail": "The specified employee does not exist."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role == "ADMIN":
            allowed = True

        elif user.role == "MANAGER":
            allowed = (
                target_employee == user
                or EmployeeProfile.objects.filter(
                    user=target_employee,
                    manager__user=user
                ).exists()
            )

        else:
            allowed = target_employee == user

        if not allowed:
            return Response(
                {
                    "detail": (
                        "You are not authorized to create a "
                        "performance goal for this employee."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(employee=target_employee)

        headers = self.get_success_headers(
            serializer.data
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        goal = self.get_object()

        if request.user.role not in {
            "ADMIN",
            "MANAGER",
            "EMPLOYEE"
        }:
            return Response(
                {
                    "detail": "You are not authorized to update goals."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if request.user.role == "ADMIN":
            return super().update(
                request,
                *args,
                **kwargs
            )

        if request.user == goal.employee:
            serializer = self.get_serializer(
                goal,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)

            serializer.save(
                employee=goal.employee
            )

            return Response(serializer.data)

        if request.user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=goal.employee,
                manager__user=request.user
            ).exists()

            if is_direct_report:
                serializer = self.get_serializer(
                    goal,
                    data=request.data
                )
                serializer.is_valid(
                    raise_exception=True
                )

                serializer.save(
                    employee=goal.employee
                )

                return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "You are not authorized to update "
                    "this performance goal."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def partial_update(self, request, *args, **kwargs):
        goal = self.get_object()

        if request.user.role == "ADMIN":
            return super().partial_update(
                request,
                *args,
                **kwargs
            )

        if request.user == goal.employee:
            serializer = self.get_serializer(
                goal,
                data=request.data,
                partial=True
            )
            serializer.is_valid(
                raise_exception=True
            )

            serializer.save(
                employee=goal.employee
            )

            return Response(serializer.data)

        if request.user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=goal.employee,
                manager__user=request.user
            ).exists()

            if is_direct_report:
                serializer = self.get_serializer(
                    goal,
                    data=request.data,
                    partial=True
                )
                serializer.is_valid(
                    raise_exception=True
                )

                serializer.save(
                    employee=goal.employee
                )

                return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "You are not authorized to update "
                    "this performance goal."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        goal = self.get_object()

        if request.user.role == "ADMIN":
            return super().destroy(
                request,
                *args,
                **kwargs
            )

        if request.user == goal.employee:
            return super().destroy(
                request,
                *args,
                **kwargs
            )

        if request.user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=goal.employee,
                manager__user=request.user
            ).exists()

            if is_direct_report:
                return super().destroy(
                    request,
                    *args,
                    **kwargs
                )

        return Response(
            {
                "detail": (
                    "You are not authorized to delete "
                    "this performance goal."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

class AppraisalViewSet(viewsets.ModelViewSet):
    """
    Secure Appraisal API.

    READ access:
    - ADMIN: all appraisals.
    - MANAGER: own appraisals and appraisals belonging to direct reports.
    - EMPLOYEE: own appraisals only.

    WRITE access:
    - ADMIN: can manage all appraisals.
    - MANAGER: can manage appraisals for direct reports.
    - EMPLOYEE: read-only access to own appraisals.

    The employee being appraised is validated server-side.
    The reviewer is assigned server-side.
    """

    serializer_class = AppraisalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return Appraisal.objects.all().order_by(
                "-reviewed_at"
            )

        if user.role == "MANAGER":
            return Appraisal.objects.filter(
                Q(employee=user)
                | Q(
                    employee__employee_profile__manager__user=user
                )
            ).distinct().order_by(
                "-reviewed_at"
            )

        return Appraisal.objects.filter(
            employee=user
        ).order_by(
            "-reviewed_at"
        )

    def create(self, request, *args, **kwargs):
        user = request.user

        employee_id = request.data.get("employee")

        if not employee_id:
            return Response(
                {"detail": "The employee field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            employee_id = int(employee_id)
        except (TypeError, ValueError):
            return Response(
                {"detail": "The employee field must contain a valid employee ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from accounts.models import User

        target_employee = User.objects.filter(
            id=employee_id
        ).first()

        if target_employee is None:
            return Response(
                {"detail": "The specified employee does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role == "ADMIN":
            allowed = True
        elif user.role == "MANAGER":
            allowed = EmployeeProfile.objects.filter(
                user=target_employee,
                manager__user=user
            ).exists()
        else:
            allowed = False

        if not allowed:
            return Response(
                {
                    "detail": (
                        "You are not authorized to create an appraisal "
                        "for this employee."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(
            employee=target_employee,
            reviewer=user
        )

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        appraisal = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=appraisal.employee,
                manager__user=user
            ).exists()

            if not is_direct_report:
                return Response(
                    {
                        "detail": (
                            "You are not authorized to update "
                            "this appraisal."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(
                appraisal,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)

            serializer.save(
                employee=appraisal.employee,
                reviewer=appraisal.reviewer
            )

            return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "Employees have read-only access to appraisals."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def partial_update(self, request, *args, **kwargs):
        appraisal = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().partial_update(request, *args, **kwargs)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=appraisal.employee,
                manager__user=user
            ).exists()

            if not is_direct_report:
                return Response(
                    {
                        "detail": (
                            "You are not authorized to update "
                            "this appraisal."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.get_serializer(
                appraisal,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)

            serializer.save(
                employee=appraisal.employee,
                reviewer=appraisal.reviewer
            )

            return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "Employees have read-only access to appraisals."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        appraisal = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().destroy(request, *args, **kwargs)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=appraisal.employee,
                manager__user=user
            ).exists()

            if is_direct_report:
                return super().destroy(request, *args, **kwargs)

        return Response(
            {
                "detail": (
                    "You are not authorized to delete "
                    "this appraisal."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )