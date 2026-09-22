from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='audit_logs')
    action = models.CharField(max_length=255) # e.g. "APPROVED_LEAVE", "UPDATED_SALARY"
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "System/Anonymous"
        return f"[{self.timestamp}] {username}: {self.action}"