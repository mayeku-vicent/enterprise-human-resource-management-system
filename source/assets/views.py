from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

from .models import CompanyAsset
from .serializers import CompanyAssetSerializer

from accounts.models import EmployeeProfile


class CompanyAssetViewSet(viewsets.ModelViewSet):
    """
    Secure Company Asset API.

    READ access:
    - ADMIN: all assets.
    - MANAGER: own assets and assets assigned to direct reports.
    - EMPLOYEE: assets assigned to themselves.

    WRITE access:
    - ADMIN only.
    """

    serializer_class = CompanyAssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.role == "ADMIN":
            return CompanyAsset.objects.all().order_by("name")

        if user.role == "MANAGER":
            return CompanyAsset.objects.filter(
                Q(assigned_to=user)
                | Q(
                    assigned_to__employee_profile__manager__user=user
                )
            ).distinct().order_by("name")

        return CompanyAsset.objects.filter(
            assigned_to=user
        ).order_by("name")

    def create(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return Response(
                {
                    "detail": (
                        "Only Administrators are authorized "
                        "to create company assets."
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
                        "to update company assets."
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
                        "to update company assets."
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
                        "to delete company assets."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().destroy(request, *args, **kwargs)