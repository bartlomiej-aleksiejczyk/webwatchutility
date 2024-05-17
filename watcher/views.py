from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .tasks import make_request
from webwatchutility.celery import app

def set_periodic_task(request):
    if request.method == 'POST':
        endpoint = request.POST.get('endpoint')
        interval = request.POST.get('interval')

        try:
            if endpoint and interval:
                interval = int(interval)

                task_name = f"make_request_{endpoint.replace('.', '_')}_{interval}"

                app.conf.beat_schedule[task_name] = {
                    'task': 'watcher.tasks.make_request',
                    'schedule': interval,
                    'args': (endpoint,),
                }
                return HttpResponse(f"Task {task_name} scheduled successfully.")
            else:
                raise ValueError("Endpoint or interval is missing.")
        except ValueError as e:
            return HttpResponse(str(e), status=400)

    tasks = app.conf.beat_schedule
    return render(request, 'task_status.html', {'tasks': tasks})

