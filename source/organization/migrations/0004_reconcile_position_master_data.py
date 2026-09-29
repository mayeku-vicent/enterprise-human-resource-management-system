from django.db import migrations


def reconcile_position_master_data(apps, schema_editor):
    Position = apps.get_model("organization", "Position")
    JobTitle = apps.get_model("organization", "JobTitle")
    JobGrade = apps.get_model("organization", "JobGrade")

    for position in Position.objects.all():
        if position.title:
            job_title, _ = JobTitle.objects.get_or_create(
                name=position.title.strip(),
                defaults={
                    "code": position.title.strip().upper().replace(" ", "_")[:30],
                    "is_active": True,
                },
            )
            position.job_title_id = job_title.id

        if position.grade:
            grade_name = position.grade.strip()
            job_grade, _ = JobGrade.objects.get_or_create(
                name=grade_name,
                defaults={
                    "code": grade_name.upper().replace(" ", "_")[:30],
                    "is_active": True,
                },
            )
            position.job_grade_id = job_grade.id

        position.save(update_fields=["job_title", "job_grade"])


def reverse_reconciliation(apps, schema_editor):
    Position = apps.get_model("organization", "Position")
    Position.objects.update(
        job_title=None,
        job_grade=None,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("organization", "0003_department_division_position_cost_center_and_more"),
    ]

    operations = [
        migrations.RunPython(
            reconcile_position_master_data,
            reverse_reconciliation,
        ),
    ]
