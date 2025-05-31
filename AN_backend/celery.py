import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AN_backend.settings')
app = Celery('AN_backend')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['api'])