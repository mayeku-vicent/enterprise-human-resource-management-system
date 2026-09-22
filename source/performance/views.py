from rest_framework import viewsets, permissions
from .models import PerformanceGoal, Appraisal
from .serializers import PerformanceGoalSerializer, AppraisalSerializer

class PerformanceGoalViewSet(viewsets.ModelViewSet):
    queryset = PerformanceGoal.objects.all()
    serializer_class = PerformanceGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

class AppraisalViewSet(viewsets.ModelViewSet):
    queryset = Appraisal.objects.all()
    serializer_class = AppraisalSerializer
    permission_classes = [permissions.IsAuthenticated]