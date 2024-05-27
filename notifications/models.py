from django.db import models

from users.models import NotificationEmailAddress
from watcher.models import ScheduledTask


class NotificationPartial(models.Model):
    notification_email_address = models.ForeignKey(
        NotificationEmailAddress, on_delete=models.CASCADE
    )
    scheduled_task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.notification_email_address.email}"
