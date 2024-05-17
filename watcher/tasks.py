from celery import shared_task
import requests
import logging

logger = logging.getLogger('django.info')
@shared_task
def make_request(endpoint):
    logger.info('Action made to endpoint: %s', endpoint)
    response = requests.get(endpoint)
    print("ddf")
    return response.text