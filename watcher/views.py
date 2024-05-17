from django.shortcuts import render
from django.http import JsonResponse
from .tasks import make_request
from myproject.celery import app

def set_periodic_task(request):
    endpoint = request.GET.get('endpoint')
    interval = request.GET.get('interval', type=int)
    if endpoint and interval:
        # Here you can adjust the periodic task setting
        # This is a placeholder: you need to properly handle periodic tasks
        app.conf.beat_schedule = {
            'make_request_every_interval': {
                'task': 'myapp.tasks.make_request',
                'schedule': interval,
                'args': (endpoint,),
            },
        }
        return JsonResponse({'status': 'scheduled', 'endpoint': endpoint, 'interval': interval})
    else:
        return JsonResponse({'error': 'Invalid parameters'}, status=400)
