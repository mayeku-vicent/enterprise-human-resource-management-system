from django.contrib import admin
from .models import JobVacancy, Applicant

admin.site.register(JobVacancy)
admin.site.register(Applicant)