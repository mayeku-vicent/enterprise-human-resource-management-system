from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Branch(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="branches",
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company", "code"],
                name="unique_branch_code_per_company",
            ),
            models.UniqueConstraint(
                fields=["company", "name"],
                name="unique_branch_name_per_company",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.company.name})"


class Location(models.Model):
    branch = models.ForeignKey(
        Branch,
        on_delete=models.CASCADE,
        related_name="locations",
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)
    address = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["branch", "code"],
                name="unique_location_code_per_branch",
            ),
            models.UniqueConstraint(
                fields=["branch", "name"],
                name="unique_location_name_per_branch",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.branch.name})"


class Division(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    department = models.ForeignKey(
        "Department",
        on_delete=models.CASCADE,
        related_name="sections",
    )
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["department", "code"],
                name="unique_section_code_per_department",
            ),
            models.UniqueConstraint(
                fields=["department", "name"],
                name="unique_section_name_per_department",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class JobTitle(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class JobGrade(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CostCenter(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=30, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Department(models.Model):
    division = models.ForeignKey(
        Division,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="departments",
    )

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(
        max_length=20,
        unique=True,
        help_text="Short code e.g. ENG, HR",
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    """
    Represents a specific job title or role within a department.
    """

    title = models.CharField(max_length=100)
    section = models.ForeignKey(
        Section,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
    )
    job_title = models.ForeignKey(
        JobTitle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
    )
    job_grade = models.ForeignKey(
        JobGrade,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
    )
    cost_center = models.ForeignKey(
        CostCenter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="positions",
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="positions",
    )
    grade = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Job grade level e.g. L1, L2, Executive",
    )
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.department.name})"
