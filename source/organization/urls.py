from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BranchViewSet,
    CompanyViewSet,
    CostCenterViewSet,
    DepartmentViewSet,
    DivisionViewSet,
    JobGradeViewSet,
    JobTitleViewSet,
    LocationViewSet,
    PositionViewSet,
    SectionViewSet,
    OrganizationChartAPIView,
    organization_management_view,
)


router = DefaultRouter()

router.register(r"companies", CompanyViewSet)
router.register(r"branches", BranchViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"divisions", DivisionViewSet)
router.register(r"departments", DepartmentViewSet)
router.register(r"sections", SectionViewSet)
router.register(r"positions", PositionViewSet)
router.register(r"job-titles", JobTitleViewSet)
router.register(r"job-grades", JobGradeViewSet)
router.register(r"cost-centers", CostCenterViewSet)


urlpatterns = [
    path("organization-chart/", OrganizationChartAPIView.as_view(), name="organization-chart"),
    path("", include(router.urls)),
]


