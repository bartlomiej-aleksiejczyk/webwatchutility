from celery import shared_task
import requests

@shared_task
def make_request(endpoint):
    response = requests.get(endpoint)
    return response.text