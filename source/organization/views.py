from rest_framework import viewsets
from .models import Department, Position
from .serializers import DepartmentSerializer, PositionSerializer

class DepartmentViewSet(viewsets.ModelViewSet):
   
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer


class PositionViewSet(viewsets.ModelViewSet):
  
    queryset = Position.objects.all().order_by('title')
    serializer_class = PositionSerializer