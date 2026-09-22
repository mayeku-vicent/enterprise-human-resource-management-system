from django.db import migrations


def migrate_employee_profiles(apps, schema_editor):
    EmployeeProfile = apps.get_model("accounts", "EmployeeProfile")
    LegacyEmployeeProfile = apps.get_model("hrms_modules", "EmployeeProfile")

    for legacy_profile in LegacyEmployeeProfile.objects.all():
        EmployeeProfile.objects.update_or_create(
            user_id=legacy_profile.user_id,
            defaults={
                "employee_id": f"EMP-{legacy_profile.user_id:03d}",
                "job_title": legacy_profile.job_title,
                "phone_number": legacy_profile.phone_number,
                "date_of_joining": legacy_profile.date_joined,
                "department_id": legacy_profile.department_id,
                "position_id": legacy_profile.position_id,
                "emergency_contact": None,
            },
        )


def reverse_migrate_employee_profiles(apps, schema_editor):
    EmployeeProfile = apps.get_model("accounts", "EmployeeProfile")
    EmployeeProfile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_employeeprofile_job_title"),
        (
            "hrms_modules",
            "0002_remove_expenseclaim_title_employeeprofile_position_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(
            migrate_employee_profiles,
            reverse_migrate_employee_profiles,
        ),
    ]