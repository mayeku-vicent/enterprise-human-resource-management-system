from rest_framework import serializers
from .models import Department, Position

class PositionSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')

    class Meta:
        model = Position
        fields = ['id', 'title', 'department', 'department_name', 'grade', 'description']

class DepartmentSerializer(serializers.ModelSerializer):
    positions = PositionSerializer(many=True, read_only=True)
    employee_count = serializers.IntegerField(source='employees.count', read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'employee_count', 'positions', 'created_at']