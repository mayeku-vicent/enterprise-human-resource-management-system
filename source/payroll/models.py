from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class EmployeeSalary(models.Model):
    employee = models.OneToOneField(User, on_delete=models.CASCADE, related_name='salary_profile')
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    allowances = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.employee.username} - Salary Profile"

class Payslip(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payslips')
    pay_period = models.CharField(max_length=50) # e.g., "September 2026"
    net_pay = models.DecimalField(max_digits=12, decimal_places=2)
    is_paid = models.BooleanField(default=False)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payslip for {self.employee.username} ({self.pay_period})"