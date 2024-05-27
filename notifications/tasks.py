from django.core.mail import send_mass_mail
from django.db.models import Count
from django.conf import settings
from celery.utils.log import get_task_logger
from celery import shared_task

from users.models import NotificationEmailAddress

from .models import NotificationPartial


logger = get_task_logger(__name__)


@shared_task
def send_batch_notifications():
    emails_with_partials = NotificationEmailAddress.objects.annotate(
        count=Count("notificationpartial")
    ).filter(count__gt=0)

    messages = []
    for email in emails_with_partials:
        partials = NotificationPartial.objects.filter(communication_channel=email)
        combined_message = "\n\n".join(partial.message for partial in partials)
        messages.append(
            (
                f"Aggregated Updates",
                combined_message,
                settings.DEFAULT_FROM_EMAIL,
                [email.email],
            )
        )
        partials.delete()

    if messages:
        send_mass_mail(messages, fail_silently=False)
        logger.info("Batch emails sent successfully.")

    else:
        logger.info("No notifications to send.")
