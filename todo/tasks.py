from celery import shared_task
from django.utils import timezone
from .models import Task
from user_profile.models import Notification
from django.urls import reverse

@shared_task
def check_overdue_tasks(task_id=None):  # task_id parametresini opsiyonel yapın
    if task_id:
        # Tek bir görev kontrolü
        task = Task.objects.get(id=task_id)
        if task.due_date < timezone.now() and task.status in ['todo', 'in_progress']:
            task.status = 'overdue'
            task.save()
    else:
        # Tüm görevleri kontrol et
        now = timezone.now()
        overdue_tasks = Task.objects.filter(
            due_date__lt=now,
            status__in=['todo', 'in_progress']
        )
        
        for task in overdue_tasks:
            task.status = 'overdue'
            task.save()
            
            Notification.objects.create(
                user=task.user,
                message=f'"{task.title}" görevinin teslim tarihi geçti!',
                notification_type='task',
                related_id=task.id,
                url=reverse('todo:task_detail', args=[task.id])
            )
@shared_task
def auto_complete_tasks():
    # Belirli bir süre geçtikten sonra otomatik tamamlama
    pass  # İhtiyaca göre düzenlenebilir