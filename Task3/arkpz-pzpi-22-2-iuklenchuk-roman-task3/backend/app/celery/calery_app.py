from celery import Celery
from celery.schedules import crontab

import app.celery.celeryconfig as celeryconfig

celery_app = Celery("warehouserent")
celery_app.config_from_object(celeryconfig)
celery_app.conf.accept_content = ['application/json', 'application/x-python-serialize']

