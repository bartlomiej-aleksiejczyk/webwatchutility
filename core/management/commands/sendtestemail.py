from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    help = "Sends a test email to a specified address."

    def add_arguments(self, parser):
        parser.add_argument(
            "email", type=str, help="The email address to send a test email to"
        )

    def handle(self, *args, **kwargs):
        email = kwargs["email"]
        subject = "Test Email from Django"
        message = "This is a test email sent by the Django application."
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [email]
        send_mail(subject, message, email_from, recipient_list, fail_silently=False)
        self.stdout.write(self.style.SUCCESS("Successfully sent email to %s" % email))
