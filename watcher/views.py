from django.shortcuts import render, redirect
from django.http import HttpResponse

from .services import create_scheduled_task
from .models import IntervalChoices
from .content_extraction_strategies import ContentProcessingStrategies
from .slug_transformers import dashify, deslugify


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
