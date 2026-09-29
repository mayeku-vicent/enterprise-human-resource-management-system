from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import TrainingCourse, EmployeeCertification
from .serializers import (
    TrainingCourseSerializer,
    EmployeeCertificationSerializer,
)


class TrainingCourseViewSet(viewsets.ModelViewSet):
    """
    Secure Training Course API.

    READ access:
    - ADMIN: all training courses.
    - MANAGER: active training courses only.
    - EMPLOYEE: active training courses only.

    WRITE access:
    - ADMIN: can create, update, and delete training courses.
    - MANAGER: read-only.
    - EMPLOYEE: read-only.
    """

    serializer_class = TrainingCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return TrainingCourse.objects.all().order_by("title")

        return TrainingCourse.objects.filter(
            is_active=True
        ).order_by("title")

    def create(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to create training courses."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to update training courses."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to update training courses."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to delete training courses."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)
class EmployeeCertificationViewSet(viewsets.ModelViewSet):
    """
    Secure Employee Certification API.

    READ access:
    - ADMIN: all certifications.
    - MANAGER: own certifications and certifications belonging
      to direct reports.
    - EMPLOYEE: own certifications only.

    WRITE access:
    - ADMIN: can manage all certifications.
    - MANAGER: can manage certifications of direct reports.
    - EMPLOYEE: can manage own certifications only.

    Employee ownership is always validated server-side.
    """

    serializer_class = EmployeeCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return EmployeeCertification.objects.all().order_by(
                "-issue_date"
            )

        if user.role == "MANAGER":
            return EmployeeCertification.objects.filter(
                Q(employee=user)
                | Q(
                    employee__employee_profile__manager__user=user
                )
            ).distinct().order_by(
                "-issue_date"
            )

        return EmployeeCertification.objects.filter(
            employee=user
        ).order_by(
            "-issue_date"
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
            allowed = target_employee == user

        if not allowed:
            return Response(
                {
                    "detail": (
                        "You are not authorized to create "
                        "a certification for this employee."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save(employee=target_employee)

        headers = self.get_success_headers(serializer.data)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        certification = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().update(request, *args, **kwargs)

        if user == certification.employee:
            serializer = self.get_serializer(
                certification,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(employee=certification.employee)

            return Response(serializer.data)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=certification.employee,
                manager__user=user
            ).exists()

            if is_direct_report:
                serializer = self.get_serializer(
                    certification,
                    data=request.data
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(employee=certification.employee)

                return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "You are not authorized to update "
                    "this certification."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def partial_update(self, request, *args, **kwargs):
        certification = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().partial_update(request, *args, **kwargs)

        if user == certification.employee:
            serializer = self.get_serializer(
                certification,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(employee=certification.employee)

            return Response(serializer.data)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=certification.employee,
                manager__user=user
            ).exists()

            if is_direct_report:
                serializer = self.get_serializer(
                    certification,
                    data=request.data,
                    partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(employee=certification.employee)

                return Response(serializer.data)

        return Response(
            {
                "detail": (
                    "You are not authorized to update "
                    "this certification."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )

    def destroy(self, request, *args, **kwargs):
        certification = self.get_object()
        user = request.user

        if user.role == "ADMIN":
            return super().destroy(request, *args, **kwargs)

        if user == certification.employee:
            return super().destroy(request, *args, **kwargs)

        if user.role == "MANAGER":
            is_direct_report = EmployeeProfile.objects.filter(
                user=certification.employee,
                manager__user=user
            ).exists()

            if is_direct_report:
                return super().destroy(request, *args, **kwargs)

        return Response(
            {
                "detail": (
                    "You are not authorized to delete "
                    "this certification."
                )
            },
            status=status.HTTP_403_FORBIDDEN
        )