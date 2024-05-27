from datetime import datetime

from django.core.mail import EmailMessage
from django.db.models import Count
from django.conf import settings
from django.utils.html import mark_safe

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

    email_objects = []
    for email in emails_with_partials:
        partials = NotificationPartial.objects.filter(notification_email_address=email)
        combined_message = "<br/><hr/><br/>".join(
            mark_safe(f"<div style='margin-bottom: 20px;'>{partial.message}</div>")
            for partial in partials
        )

        if partials.exists():
            task_name = partials.first().scheduled_task.name
        else:
            task_name = "No Task"
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M")

        subject = f"{task_name} Updates - {current_datetime}"

        message = EmailMessage(
            subject=subject,
            body=combined_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email.email],
            headers={"Content-Type": "text/html"},
        )
        message.content_subtype = "html"
        email_objects.append(message)
        partials.delete()

    if email_objects:
        for message in email_objects:
            message.send(fail_silently=False)
        logger.info("Batch emails sent successfully.")
    else:
        logger.info("No notifications to send.")
