from rest_framework import serializers

from .models import User, EmployeeProfile


class EmployeeProfileSerializer(serializers.ModelSerializer):
    department_name = serializers.ReadOnlyField(source="department.name")
    position_title = serializers.ReadOnlyField(source="position.title")
    organization_location_name = serializers.ReadOnlyField(
        source="organization_location.name"
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            "id",
            "employee_id",
            "phone_number",
            "date_of_joining",
            "employment_type",
            "employment_status",
            "department",
            "department_name",
            "position",
            "position_title",
            "manager",
            "location",
            "organization_location",
            "organization_location_name",
            "job_title",
            "emergency_contact",
        ]
        read_only_fields = [
            "id",
            "employee_id",
            "employment_status",
            "department_name",
            "position_title",
        ]


class UserSerializer(serializers.ModelSerializer):
    employee_profile = EmployeeProfileSerializer(required=False)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "employee_profile",
        ]
        read_only_fields = [
            "id",
            "username",
            "role",
            "is_active",
        ]

    def create(self, validated_data):
        profile_data = validated_data.pop("employee_profile", None)

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
        )

        if profile_data:
            EmployeeProfile.objects.create(
                user=user,
                employee_id=f"EMP-{user.id:03d}",
                **profile_data,
            )
        else:
            EmployeeProfile.objects.create(
                user=user,
                employee_id=f"EMP-{user.id:03d}",
            )

        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop("employee_profile", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if profile_data and hasattr(instance, "employee_profile"):
            profile = instance.employee_profile

            for attr, value in profile_data.items():
                setattr(profile, attr, value)

            profile.save()

        return instance