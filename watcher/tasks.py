from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.db import DatabaseError
from .models import ScheduledTask, IntervalChoices
import requests
import random

logger = get_task_logger(__name__)

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def make_request(endpoint):
    logger.info(f'Making request to endpoint: {endpoint}')
    try:
        response = requests.get(endpoint)
        logger.info(f'Received response from endpoint: {endpoint} with status code {response.status_code}')
        return response.text
    except requests.RequestException as e:
        logger.error(f'Failed to make request to {endpoint}: {str(e)}')
        raise

@shared_task
def check_scheduled_tasks(interval):
    now = timezone.now()
    logger.info(f'Checking tasks with interval: {interval} at time: {now}')

    try:
        tasks = ScheduledTask.objects.filter(interval=interval)
    except DatabaseError as e:
        logger.error(f'Database error when fetching tasks: {str(e)}')
        raise

    logger.info(f'Found {len(tasks)} tasks to execute')

    grouped_tasks = {}
    for task in tasks:
        domain = task.endpoint.split('/')[2]
        if domain not in grouped_tasks:
            grouped_tasks[domain] = []
        grouped_tasks[domain].append(task.id)
        logger.info(f'Task grouped under domain: {domain}')

    for domain, task_ids in grouped_tasks.items():
        logger.info(f'Executing grouped tasks for domain: {domain} with {len(task_ids)} tasks')
        execute_grouped_tasks.apply_async(args=[task_ids])

@shared_task
def execute_grouped_tasks(task_ids):
    logger.info(f'Task ids: {task_ids}')
    if not isinstance(task_ids, list):
        logger.error(f'Expected list of task IDs, got {type(task_ids)}')
        raise TypeError("task_ids must be a list")

    try:
        tasks = ScheduledTask.objects.filter(id__in=task_ids)
    except DatabaseError as e:
        logger.error(f'Database error when fetching tasks for execution: {str(e)}')
        raise

    for task in tasks:
        make_request.apply_async(args=[task.endpoint], link=process_task_result.s(task.id))

@shared_task
def process_task_result(task_response, task_id):
    try:
        task = ScheduledTask.objects.get(id=task_id)
    except ScheduledTask.DoesNotExist:
        logger.error(f'Task with id {task_id} does not exist.')
        return

    task.last_run = timezone.now()
    task.latest_response = None

    if task.processing_strategy:
        strategy_cls = globals().get(task.processing_strategy)
        if strategy_cls:
            strategy = strategy_cls()
            try:
                processed_data = strategy.process(task_response, *task.additional_params)
                task.latest_response = processed_data
                task.last_successful = True
            except Exception as e:
                task.last_successful = False
                task.error_message = str(e)
                logger.error(f'Error processing task {task.id}: {str(e)}')

    try:
        task.save()
    except DatabaseError as e:
        logger.error(f'Failed to save task {task.id} after processing: {str(e)}')
        raise

    logger.info(f'Response for task {task.id} processed: {"Success" if task.last_successful else "Failed"}')
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
    logger.info(f'Scheduling next run for task {task.id} after {wait_time:.2f} seconds')
    execute_grouped_tasks.apply_async((task.id,), countdown=wait_time)
