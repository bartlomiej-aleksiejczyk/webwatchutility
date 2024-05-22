from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ScheduledTask, IntervalChoices, ProcessingStrategyChoices

# TODO: separate service layer
# TODO: RESTful endpointds
# TODO: Crud for scheduled job
# TODO: urls in app not project
def create_task(request):
    if request.method == 'POST':
        strategy = request.POST.get('strategy')
        if strategy:
            return redirect('strategy-form', strategy_name=strategy)

    interval_choices = IntervalChoices.choices()
    strategy_choices = ProcessingStrategyChoices.choices()
    return render(request, 'tasks/create.html', {'interval_choices': interval_choices, 'strategy_choices': strategy_choices})


def strategy_form(request, strategy_name):
    if request.method == 'POST':
        endpoint = request.POST.get('endpoint')
        interval = request.POST.get('interval')
        strategy = strategy_name
        additional_params = request.POST.getlist('additional_params')

        if endpoint and interval and strategy:
            ScheduledTask.objects.create(
                endpoint=endpoint,
                interval=interval,
                processing_strategy=strategy,
                additional_params=additional_params
            )
            return HttpResponse(f"Task for {endpoint} with strategy {strategy} scheduled successfully.")
        else:
            return HttpResponse("Missing required fields.", status=400)

    interval_choices = IntervalChoices.choices()
    return render(request, 'tasks/strategy_form.html', {
        'strategy_name': strategy_name,
        'interval_choices': interval_choices
    })
