from celery import shared_task, group
from django.utils import timezone
from .models import ScheduledTask, IntervalChoices
import requests
import time
import random
import logging

logger = logging.getLogger('django.info')

@shared_task
def check_scheduled_tasks(interval):
    now = timezone.now()
    tasks = ScheduledTask.objects.filter(interval=interval, last_run__lt=now)
    
    grouped_tasks = {}
    for task in tasks:
        domain = task.endpoint.split('/')[2]
        if domain not in grouped_tasks:
            grouped_tasks[domain] = []
        grouped_tasks[domain].append(task)

    for domain, tasks in grouped_tasks.items():
        execute_grouped_tasks.apply_async(args=[tasks])

@shared_task
def execute_grouped_tasks(tasks):
    for task in tasks:
        make_request.apply_async(args=[task.endpoint])
        task.last_run = timezone.now()
        task.save()
        
        interval_seconds = {
            IntervalChoices.FIVE_MINUTES.value: 300,
            IntervalChoices.FIFTEEN_MINUTES.value: 900,
            IntervalChoices.THIRTY_MINUTES.value: 1800,
            IntervalChoices.ONE_HOUR.value: 3600,
            IntervalChoices.TWO_HOURS.value: 7200,
            IntervalChoices.FOUR_HOURS.value: 14400,
            IntervalChoices.EIGHT_HOURS.value: 28800,
            IntervalChoices.TWENTY_FOUR_HOURS.value: 86400,
        }
        wait_time = random.uniform(0, 0.1 * interval_seconds[task.interval])
        time.sleep(wait_time)
