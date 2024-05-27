import enum


from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField

from users.models import NotificationEmailAddress

from .domain.content_extraction_strategies import ContentProcessingStrategies


class IntervalChoices(enum.Enum):
    FIVE_MINUTES = "5min"
    FIFTEEN_MINUTES = "15min"
    THIRTY_MINUTES = "30min"
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    FOUR_HOURS = "4h"
    EIGHT_HOURS = "8h"
    TWENTY_FOUR_HOURS = "24h"

    @classmethod
    def choices(cls):
        return [(key.value, key.name.replace("_", " ").title()) for key in cls]


class ScheduledTask(models.Model):
    endpoint = models.URLField()
    interval = models.CharField(max_length=10, choices=IntervalChoices.choices())
    last_run = models.DateTimeField(null=True, blank=True)
    latest_response = models.TextField(null=True, blank=True)
    last_successful = models.BooleanField(default=True)
    error_message = models.TextField(null=True, blank=True)
    processing_strategy = models.CharField(
        max_length=50,
        choices=ContentProcessingStrategies.choices(),
        blank=True,
        null=True,
    )
    additional_params = ArrayField(
        models.CharField(max_length=255), blank=True, null=True
    )
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=False, default=timezone.now)

    def __str__(self):
        return f"{self.endpoint})"


class Subscription(models.Model):
    communication_channel = models.ForeignKey(
        NotificationEmailAddress,
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )
    scheduled_task = models.ForeignKey(
        ScheduledTask, on_delete=models.CASCADE, related_name="subscriptions"
    )

    def __str__(self):
        return f"{self.communication_channel} subscribed to {self.scheduled_task}"
