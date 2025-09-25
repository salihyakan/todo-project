from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Task
from dashboard.models import CalendarEvent
from user_profile.models import Notification
from django.urls import reverse
from .tasks import check_overdue_tasks
from config import settings
from user_profile.tasks import send_notification, send_email_notification



@receiver(post_save, sender=Task)
def update_task_calendar_event(sender, instance, created, **kwargs):
    CalendarEvent.objects.update_or_create(
        related_task=instance,
        defaults={
            'user': instance.user,
            'title': instance.title,
            'start': instance.due_date,
            'description': instance.description,
            'event_type': 'task'
        }
    )

@receiver(post_delete, sender=Task)
def delete_task_calendar_event(sender, instance, **kwargs):
    CalendarEvent.objects.filter(related_task=instance).delete()

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created:
        # Yeni görev oluşturulduğunda
        message = f"Yeni görev: {instance.title}"
        Notification.objects.create(
            user=instance.user,
            message=message,
            notification_type='task',
            related_id=instance.id,
            url=reverse('todo:task_detail', args=[instance.id])
        )
    elif not created and instance.status == 'completed':
        # Görev tamamlandığında
        message = f"Tebrikler! '{instance.title}' görevini tamamladınız."
        Notification.objects.create(
            user=instance.user,
            message=message,
            notification_type='task',
            related_id=instance.id,
            url=reverse('todo:task_detail', args=[instance.id])
        )

@receiver(post_delete, sender=Task)
def delete_task_notification(sender, instance, **kwargs):
    # Görev silindiğinde
    message = f"'{instance.title}' görevi silindi."
    Notification.objects.create(
        user=instance.user,
        message=message,
        notification_type='task'
    )

@receiver(post_save, sender=Task)
def schedule_task_check(sender, instance, created, **kwargs):
    if created and settings.DEBUG:
        try:
            check_overdue_tasks.apply_async(countdown=300)
        except Exception as e:
            print(f"Celery task scheduling error: {e}")

@receiver(post_save, sender=Task)
def task_created_or_updated(sender, instance, created, **kwargs):
    if created:
        # Uygulama içi bildirim
        send_notification.delay(
            instance.user.id,
            f"Yeni görev: {instance.title}",
            'task',
            instance.id
        )
        
        # E-posta bildirimi (opsiyonel)
        if instance.user.profile.email_notifications:
            send_email_notification.delay(
                instance.user.id,
                "Yeni Görev Oluşturuldu",
                f"'{instance.title}' adlı yeni bir görev oluşturdunuz.\nSon tarih: {instance.due_date.strftime('%d.%m.%Y %H:%M')}"
            )
    elif instance.status == 'completed':
        send_notification.delay(
            instance.user.id,
            f"Görev tamamlandı: {instance.title}",
            'task',
            instance.id
        )

@receiver(post_delete, sender=Task)
def task_deleted(sender, instance, **kwargs):
    send_notification.delay(
        instance.user.id,
        f"Görev silindi: {instance.title}",
        'task'
    )