from django.shortcuts import render, redirect
from django.http import HttpResponse
from .services import create_scheduled_task
from .models import IntervalChoices
from .content_extraction_strategies import ContentProcessingStrategies


def create_task(request):
    if request.method == "POST":
        strategy = request.POST.get("strategy")
        if strategy:
            return redirect("strategy-form", strategy_name=strategy)

    interval_choices = IntervalChoices.choices()
    strategy_choices = ContentProcessingStrategies.choices()
    return render(
        request,
        "tasks/create.html",
        {"interval_choices": interval_choices, "strategy_choices": strategy_choices},
    )


def strategy_form(request, strategy_name):
    if request.method == "POST":
        endpoint = request.POST.get("endpoint")
        interval = request.POST.get("interval")
        additional_params = request.POST.getlist("additional_params")

        if endpoint and interval and strategy_name:
            task = create_scheduled_task(
                endpoint, interval, strategy_name, additional_params
            )
            return HttpResponse(
                f"Task for {endpoint} with strategy {strategy_name} scheduled successfully."
            )
        else:
            return HttpResponse("Missing required fields.", status=400)

    interval_choices = IntervalChoices.choices()
    return render(
        request,
        "tasks/strategy_form.html",
        {"strategy_name": strategy_name, "interval_choices": interval_choices},
    )
