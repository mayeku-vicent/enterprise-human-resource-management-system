from rest_framework import viewsets, permissions
from .models import TrainingCourse, EmployeeCertification
from .serializers import TrainingCourseSerializer, EmployeeCertificationSerializer

class TrainingCourseViewSet(viewsets.ModelViewSet):
    queryset = TrainingCourse.objects.all()
    serializer_class = TrainingCourseSerializer
    permission_classes = [permissions.IsAuthenticated]

class EmployeeCertificationViewSet(viewsets.ModelViewSet):
    queryset = EmployeeCertification.objects.all()
    serializer_class = EmployeeCertificationSerializer
    permission_classes = [permissions.IsAuthenticated]