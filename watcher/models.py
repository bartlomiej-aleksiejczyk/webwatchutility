from celery import shared_task
from django.utils import timezone
from .models import ScheduledTask, IntervalChoices
import requests
import random

@shared_task
def make_request(endpoint):
    try:
        print(f'Making request to endpoint: {endpoint}')
        response = requests.get(endpoint)
        response.raise_for_status()
        print(f'Received successful response from endpoint: {endpoint} with status code {response.status_code}')
        return process_response(response.text)
    except requests.RequestException as e:
        print(f'Error requesting endpoint: {endpoint} with error {str(e)}')
        return {'success': False, 'error': str(e)}

def process_response(response):
    return {'success': True, 'data': response}

@shared_task
def check_scheduled_tasks(interval):
    now = timezone.now()
    print(f'Checking tasks with interval: {interval} at time: {now}')
    tasks = ScheduledTask.objects.filter(interval=interval)
    print(f'Found {len(tasks)} tasks to execute')
    grouped_tasks = {}
    for task in tasks:
        domain = task.endpoint.split('/')[2]
        if domain not in grouped_tasks:
            grouped_tasks[domain] = []
        grouped_tasks[domain].append(task.id)
        print(f'Task grouped under domain: {domain}')
    for domain, task_ids in grouped_tasks.items():
        print(f'Executing grouped tasks for domain: {domain} with {len(task_ids)} tasks')
        execute_grouped_tasks.apply_async(args=[task_ids])

@shared_task
def execute_grouped_tasks(task_ids):
    tasks = ScheduledTask.objects.filter(id__in=task_ids)
    for task in tasks:
        make_request.apply_async(args=[task.endpoint], link=process_task_result.s(task.id))

@shared_task
def process_task_result(task_response, task_id):
    task = ScheduledTask.objects.get(id=task_id)
    task.last_run = timezone.now()
    if task_response.get('success'):
        task.latest_response = task_response['data']
        task.last_successful = True
        task.error_message = None
    else:
        task.latest_response = None
        task.last_successful = False
        task.error_message = task_response['error']
    task.save()
    print(f'Response for task {task.id} processed: {"Success" if task.last_successful else "Failed"}')
    schedule_next_run(task)

def schedule_next_run(task):
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
    print(f'Scheduling next run for task {task.id} after {wait_time:.2f} seconds')
    execute_grouped_tasks.apply_async((task.id,), countdown=wait_time)
