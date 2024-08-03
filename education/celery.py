# education/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установить модуль настроек по умолчанию для 'celery'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'education.settings')

app = Celery('education')

# Использовать настройки Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически искать задачи в приложениях Django
app.autodiscover_tasks()


