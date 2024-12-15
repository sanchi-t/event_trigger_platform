from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_trigger_platform.settings')
app = Celery('event_trigger_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

