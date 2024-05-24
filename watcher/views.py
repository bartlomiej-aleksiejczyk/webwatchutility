from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect
from django.urls import reverse

from .domain.services import create_scheduled_task
from .models import IntervalChoices, ScheduledTask
from .domain.content_extraction_strategies import ContentProcessingStrategies
from .slug_transformers import dashify, deslugify


# TODO: Comeback button
def choose_strategy(request):
    if request.method == "POST":
        strategy = request.POST.get("strategy")
        if strategy:
            strategy_slug = dashify(strategy)
            return redirect("schedule_task", strategy_name=strategy_slug)

    interval_choices = IntervalChoices.choices()
    strategy_choices = ContentProcessingStrategies.choices()
    return render(
        request,
        "watch-tasks/strategy_form.html",
        {"interval_choices": interval_choices, "strategy_choices": strategy_choices},
    )


def schedule_task(request, strategy_name):
    strategy_name_original = deslugify(strategy_name)

    if request.method == "POST":
        endpoint = request.POST.get("endpoint")
        interval = request.POST.get("interval")
        additional_params = request.POST.getlist("additional_params")

        if endpoint and interval and strategy_name:
            task = create_scheduled_task(
                endpoint, interval, strategy_name_original, additional_params
            )
            return HttpResponse(
                f"Task for {endpoint} with strategy {strategy_name} scheduled successfully."
            )
        else:
            return HttpResponse("Missing required fields.", status=400)

    interval_choices = IntervalChoices.choices()
    return render(
        request,
        "watch-tasks/task_form.html",
        {"strategy_name": strategy_name_original, "interval_choices": interval_choices},
    )


def list_tasks(request):
    task_list = ScheduledTask.objects.all().order_by("created_at", "endpoint", "id")
    paginator = Paginator(task_list, 10)

    page = request.GET.get("page")
    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    return render(request, "watch-tasks/list_tasks.html", {"tasks": tasks})


def task_delete(request, task_id):
    task = get_object_or_404(ScheduledTask, pk=task_id)
    if request.method == "POST":
        task.delete()
        return redirect("list_tasks")
    return render(request, "watch-tasks/task_confirm_delete.html", {"task": task})


def toggle_task_enabled(request, task_id):
    task = get_object_or_404(ScheduledTask, pk=task_id)
    if request.method == "POST":
        task.is_enabled = not task.is_enabled
        task.save()

        return HttpResponseRedirect(
            request.META.get("HTTP_REFERER", reverse("list_tasks"))
        )

    return redirect("task_list")


def task_detail(request, task_id):
    task = get_object_or_404(ScheduledTask, pk=task_id)
    strategy_choices = {
        choice.value: choice.description for choice in ContentProcessingStrategies
    }

    return render(
        request,
        "watch-tasks/task_detail.html",
        {
            "task": task,
            "strategy_description": strategy_choices.get(task.processing_strategy),
        },
    )
