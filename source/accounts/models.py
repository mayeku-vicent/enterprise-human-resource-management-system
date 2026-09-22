from django.contrib.auth.models import AbstractUser
from django.db import models
from organization.models import Department, Position


class User(AbstractUser):

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        MANAGER = 'MANAGER', 'Manager'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        help_text="Designates the user role in the enterprise system."
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class EmployeeProfile(models.Model):

    class EmploymentType(models.TextChoices):
        FULL_TIME = 'FULL_TIME', 'Full Time'
        PART_TIME = 'PART_TIME', 'Part Time'
        CONTRACT = 'CONTRACT', 'Contract'
        TEMPORARY = 'TEMPORARY', 'Temporary'
        INTERN = 'INTERN', 'Intern'

    class EmploymentStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        PROBATION = 'PROBATION', 'Probation'
        ON_LEAVE = 'ON_LEAVE', 'On Leave'
        SUSPENDED = 'SUSPENDED', 'Suspended'
        RESIGNED = 'RESIGNED', 'Resigned'
        TERMINATED = 'TERMINATED', 'Terminated'
        RETIRED = 'RETIRED', 'Retired'
        INACTIVE = 'INACTIVE', 'Inactive'

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='employee_profile'
    )

    employee_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique company badge/ID number"
    )

    photo = models.ImageField(
        upload_to='employee_photos/',
        blank=True,
        null=True
    )

    job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    date_of_joining = models.DateField(
        blank=True,
        null=True
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        default=EmploymentStatus.ACTIVE
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employees'
    )

    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='direct_reports'
    )

    location = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    emergency_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    def __str__(self):
        return (
            f"Profile: "
            f"{self.user.get_full_name() or self.user.username} "
            f"- {self.employee_id}"
        )


class EmploymentHistory(models.Model):

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='employment_history'
    )

    employment_type = models.CharField(
        max_length=20,
        choices=EmployeeProfile.EmploymentType.choices
    )

    employment_status = models.CharField(
        max_length=20,
        choices=EmployeeProfile.EmploymentStatus.choices
    )

    job_title = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employment_history'
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employment_history'
    )

    start_date = models.DateField()

    end_date = models.DateField(
        blank=True,
        null=True
    )

    reason = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    notes = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-start_date', '-created_at']

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.job_title or 'Employment Record'} - "
            f"{self.start_date}"
        )
class EmployeeContact(models.Model):

    class ContactType(models.TextChoices):
        PERSONAL = 'PERSONAL', 'Personal'
        WORK = 'WORK', 'Work'
        ALTERNATE = 'ALTERNATE', 'Alternate'

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='contacts'
    )

    contact_type = models.CharField(
        max_length=20,
        choices=ContactType.choices,
        default=ContactType.PERSONAL
    )

    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.get_contact_type_display()} - "
            f"{self.phone_number or self.email or 'No contact details'}"
        )


class EmergencyContact(models.Model):

    employee = models.ForeignKey(
        EmployeeProfile,
        on_delete=models.CASCADE,
        related_name='emergency_contacts'
    )

    full_name = models.CharField(
        max_length=150
    )

    relationship = models.CharField(
        max_length=100
    )

    phone_number = models.CharField(
        max_length=20
    )

    alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        blank=True,
        null=True
    )

    address = models.TextField(
        blank=True,
        null=True
    )

    is_primary = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ['-is_primary', 'id']

    def __str__(self):
        return (
            f"{self.employee.employee_id} - "
            f"{self.full_name} ({self.relationship})"
        )