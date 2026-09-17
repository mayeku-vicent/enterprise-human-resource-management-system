from rest_framework import serializers
from .models import User, EmployeeProfile
from organization.serializers import DepartmentSerializer, PositionSerializer

class EmployeeProfileSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source='department.name')
    position_title = serializers.ReadOnlyField(source='position.title')

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'employee_id', 'phone_number', 'date_of_joining',
            'department', 'department_name', 'position', 'position_title',
            'emergency_contact'
        ]

class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'employee_profile']
        read_only_fields = ['id']

    def create(self, validated_data):
        profile_data = validated_data.pop('employee_profile', None)
        password = validated_data.pop('password', 'DefaultPassword123!') # default secure fallback
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        if profile_data:
            EmployeeProfile.objects.create(user=user, **profile_data)
        else:
            # Automatically create a blank profile if none provided
            EmployeeProfile.objects.create(user=user, employee_id=f"EMP-{user.id:03d}")

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('employee_profile', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data and hasattr(instance, 'employee_profile'):
            profile = instance.employee_profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance