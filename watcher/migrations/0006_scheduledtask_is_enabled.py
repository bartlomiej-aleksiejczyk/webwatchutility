# Generated by Django 5.0.6 on 2024-05-23 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('watcher', '0005_alter_scheduledtask_processing_strategy'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledtask',
            name='is_enabled',
            field=models.BooleanField(default=False),
        ),
    ]