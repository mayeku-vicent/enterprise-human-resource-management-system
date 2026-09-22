from rest_framework import serializers
from .models import TrainingCourse, EmployeeCertification

class TrainingCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCourse
        fields = '__all__'

class EmployeeCertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeCertification
        fields = '__all__'