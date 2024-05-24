from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("scheduler", "Scheduler"),
        ("subscriber", "Subscriber"),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="customer")
