from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("scheduler", "Scheduler"),
        ("subscriber", "Subscriber"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="subscriber")


class NotificationEmailAddress(models.Model):

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="communication_channels"
    )
    email = models.EmailField()

    def __str__(self):
        return f"{self.email}"
