from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import EmployeeProfile, Attendance, ExpenseClaim

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class EmployeeProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    # Safely handle department and position depending on whether they are fields or relations
    department = serializers.CharField(source='get_department_display', read_only=True) if hasattr(EmployeeProfile, 'get_department_display') else serializers.CharField(read_only=True, required=False)
    position = serializers.CharField(read_only=True, required=False)

    class Meta:
        model = EmployeeProfile
        fields = ['id', 'user', 'department', 'position', 'job_title', 'phone_number', 'date_joined']
        extra_kwargs = {
            'department': {'required': False},
            'position': {'required': False},
        }

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