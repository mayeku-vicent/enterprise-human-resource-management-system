from rest_framework import viewsets, permissions
from .models import WorkShift, EmployeeShiftAssignment
from .serializers import WorkShiftSerializer, EmployeeShiftAssignmentSerializer

class WorkShiftViewSet(viewsets.ModelViewSet):
    queryset = WorkShift.objects.all()
    serializer_class = WorkShiftSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeShiftAssignmentViewSet(viewsets.ModelViewSet):
    queryset = EmployeeShiftAssignment.objects.all()
    serializer_class = EmployeeShiftAssignmentSerializer
    permission_classes = [permissions.IsAuthenticated]