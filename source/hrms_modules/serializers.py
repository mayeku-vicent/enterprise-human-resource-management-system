from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Attendance, ExpenseClaim
from accounts.models import EmployeeProfile

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department_name = serializers.ReadOnlyField(source='department.name')
    position_title = serializers.ReadOnlyField(source='position.title')

    class Meta:
        model = EmployeeProfile
        fields = [
            'id',
            'user',
            'employee_id',
            'department',
            'department_name',
            'position',
            'position_title',
            'job_title',
            'phone_number',
            'date_of_joining',
            'emergency_contact',
        ]

class AttendanceSerializer(serializers.ModelSerializer):
    employee_username = serializers.ReadOnlyField(source='employee.username')

    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'employee_username', 'date', 'check_in_time', 'check_out_time', 'status']
        read_only_fields = ['id', 'employee', 'date', 'check_in_time']

class ExpenseClaimSerializer(serializers.ModelSerializer):
    employee_username = serializers.ReadOnlyField(source='employee.username')

    class Meta:
        model = ExpenseClaim
        fields = ['id', 'employee', 'employee_username', 'claim_type', 'amount', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'employee', 'status', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user') and request.user.is_authenticated:
            validated_data['employee'] = request.user
        return super().create(validated_data)