import random
import requests

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import DatabaseError
from .models import ScheduledTask, IntervalChoices
from .domain.services import fetch_and_group_tasks_by_domain

from .domain.content_extraction_strategies import ContentProcessingStrategies


logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def make_request(self, endpoint):
    logger.info(f"Making request to endpoint: {endpoint}")
    try:
        response = requests.get(endpoint, timeout=10)
        logger.info(
            f"Received response from endpoint: {endpoint} with status code {response.status_code}"
        )
        return response.text
    except requests.ConnectionError as e:
        logger.error(f"Failed to make request to {endpoint}: {str(e)}")
        if self.request.retries < self.max_retries:
            logger.info("Retrying...")
            raise self.retry(exc=e)
        return f"Failed after {self.max_retries} retries: {str(e)}"
    except requests.Timeout as e:
        logger.error(f"Request to {endpoint} timed out: {str(e)}")
        return "Request timed out"
    except requests.RequestException as e:
        logger.error(f"An error occurred while making request to {endpoint}: {str(e)}")
        return "An error occurred"


@shared_task
def check_scheduled_tasks(interval):
    fetch_and_group_tasks_by_domain(interval)


@shared_task
def execute_grouped_tasks(task_ids):
    if not isinstance(task_ids, list):
        logger.error(f"Expected list of task IDs, got {type(task_ids)}")
        raise TypeError("task_ids must be a list")

    if task_ids:
        task_id = task_ids.pop(0)
        try:
            task = ScheduledTask.objects.get(id=task_id)
            make_request.apply_async(
                args=[task.endpoint], link=process_task_result.s(task.id)
            )
        except ScheduledTask.DoesNotExist:
            logger.error(f"Task with id {task_id} does not exist.")

        if task_ids:
            schedule_next_run(task, remaining_task_ids=task_ids)


@shared_task
def process_task_result(task_response, task_id):
    try:
        task = ScheduledTask.objects.get(id=task_id)
    except ScheduledTask.DoesNotExist:
        logger.error(f"Task with id {task_id} does not exist.")
        return
    try:
        strategy_class = ContentProcessingStrategies.get_strategy_class(
            task.processing_strategy
        )
        strategy = strategy_class()

    except ValueError as e:
        task.last_successful = False
        task.error_message = str(e)
        logger.error(f"Error processing task {task.id}: {str(e)}")
    if strategy:
        try:
            processed_data = strategy.process(task_response, *task.additional_params)
            task.latest_response = processed_data
            task.last_successful = True
        except Exception as e:
            task.last_successful = False
            task.error_message = str(e)
            logger.error(f"Error processing task {task.id}: {str(e)}")

    try:
        task.save()
    except DatabaseError as e:
        logger.error(f"Failed to save task {task.id} after processing: {str(e)}")
        raise

    logger.info(
        f'Response for task {task.id} processed: {"Success" if task.last_successful else "Failed"}'
    )


def schedule_next_run(task, remaining_task_ids):
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
    logger.info(f"Scheduling next task execution after {wait_time:.2f} seconds")
    execute_grouped_tasks.apply_async(args=[remaining_task_ids], countdown=wait_time)
