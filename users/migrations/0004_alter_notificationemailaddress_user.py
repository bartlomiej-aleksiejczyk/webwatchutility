# Generated by Django 5.0.6 on 2024-05-27 16:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_notificationemailaddress'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notificationemailaddress',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notification_email_address', to=settings.AUTH_USER_MODEL),
        ),
    ]
