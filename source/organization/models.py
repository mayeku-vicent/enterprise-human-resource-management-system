from django.db import models

class Department(models.Model):
    
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="Short code e.g. ENG, HR")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Position(models.Model):
    """
    Represents a specific job title or role within a department (e.g., Software Engineer).
    """
    title = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='positions')
    grade = models.CharField(max_length=50, blank=True, null=True, help_text="Job grade level e.g. L1, L2, Executive")
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.department.name})"