from celery import Celery
from celery.schedules import crontab
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')
app.conf.enable_utc = False
app.conf.timezone = 'Europe/Istanbul'

# Django settings'den Celery ayarlarını al
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tüm uygulamalardaki tasks.py dosyalarını otomatik keşfet
app.autodiscover_tasks()

# Beat Schedule
app.conf.beat_schedule = {
    'check-overdue-tasks-every-minute': {
        'task': 'todo.tasks.check_overdue_tasks',
        'schedule': crontab(minute='*'),
    },
    'send-daily-reminders': {
        'task': 'dashboard.tasks.send_daily_reminders',
        'schedule': crontab(hour=8, minute=0),
    },
}