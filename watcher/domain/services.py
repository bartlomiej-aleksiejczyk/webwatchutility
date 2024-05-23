from django.db import DatabaseError
from ..models import ScheduledTask


def create_scheduled_task(endpoint, interval, strategy, additional_params):
    try:
        task = ScheduledTask.objects.create(
            endpoint=endpoint,
            interval=interval,
            processing_strategy=strategy,
            additional_params=additional_params,
        )
        return task
    except DatabaseError as e:
        raise


def fetch_and_group_tasks_by_domain(interval):
    from ..tasks import execute_grouped_tasks

    tasks = ScheduledTask.objects.filter(interval=interval)
    grouped_tasks = {}
    for task in tasks:
        domain = task.endpoint.split("/")[2]
        if domain not in grouped_tasks:
            grouped_tasks[domain] = []
        grouped_tasks[domain].append(task.id)
    for domain, task_ids in grouped_tasks.items():
        print(f"Task idki: {task_ids}")
        execute_grouped_tasks.apply_async(args=[task_ids])
    return grouped_tasks
