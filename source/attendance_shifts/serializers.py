from rest_framework import serializers
from .models import WorkShift, EmployeeShiftAssignment

class WorkShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkShift
        fields = '__all__'

class EmployeeShiftAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeShiftAssignment
        fields = '__all__'