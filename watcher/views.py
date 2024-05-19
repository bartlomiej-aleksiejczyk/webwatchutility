from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import ScheduledTask, IntervalChoices

def set_periodic_task(request):
    if request.method == 'POST':
        endpoint = request.POST.get('endpoint')
        interval = request.POST.get('interval')
        
        if endpoint and interval:
            ScheduledTask.objects.create(endpoint=endpoint, interval=interval)
            return HttpResponse(f"Task for {endpoint} scheduled every {interval} successfully.")
        else:
            return HttpResponse("Endpoint or interval is missing.", status=400)

    tasks = ScheduledTask.objects.all()
    interval_choices = IntervalChoices.choices()
    return render(request, 'task_status.html', {'tasks': tasks, 'interval_choices': interval_choices})
