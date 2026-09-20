from rest_framework import serializers
from .models import LeaveRequest

class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_username = serializers.ReadOnlyField(source='employee.username', default='')

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'employee', 'employee_username', 'leave_type', 
            'start_date', 'end_date', 'reason', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'employee', 'status', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['employee'] = request.user
        return super().create(validated_data)