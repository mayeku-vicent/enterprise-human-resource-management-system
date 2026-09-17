from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, PositionViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet)
router.register(r'positions', PositionViewSet)

urlpatterns = [
    path('', include(router.urls)),
]