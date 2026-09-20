from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseClaimViewSet

router = DefaultRouter()
router.register(r'', ExpenseClaimViewSet, basename='expenseclaim')

urlpatterns = [
    path('', include(router.urls)),
]