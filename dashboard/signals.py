from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CalendarEvent
from user_profile.tasks import send_notification, send_email_notification
from datetime import timedelta
from django.utils import timezone
from celery import current_app
from .tasks import schedule_event_reminder

@receiver(post_save, sender=CalendarEvent)
def event_created_or_updated(sender, instance, created, **kwargs):
    # Yeni etkinlik bildirimi
    if created:
        send_notification.delay(
            instance.user.id,
            f"Yeni etkinlik: {instance.title} - {instance.start_date.strftime('%d.%m.%Y %H:%M')}",
            'calendar',
            instance.id,
            instance.get_absolute_url()
        )
    
    # Hatırlatıcı planlama
    if instance.reminder and not instance.reminder_sent:
        reminder_time = instance.start_date - timedelta(minutes=instance.reminder)
        
        if reminder_time > timezone.now():
            schedule_event_reminder.apply_async(
                args=[instance.id],
                eta=reminder_time
            )
        else:
            # Hatırlatıcı zamanı geçmişse hemen gönder
            send_notification.delay(
                instance.user.id,
                f"Etkinlik hatırlatıcı: {instance.title} başlamak üzere!",
                'calendar',
                instance.id,
                instance.get_absolute_url()
            )
            if instance.user.profile.email_notifications:
                send_email_notification.delay(
                    instance.user.id,
                    "Etkinlik Hatırlatıcı",
                    f"'{instance.title}' etkinliği başlamak üzere!"
                )
            instance.reminder_sent = True
            instance.save()

@receiver(post_delete, sender=CalendarEvent)
def event_deleted(sender, instance, **kwargs):
    send_notification.delay(
        instance.user.id,
        f"Etkinlik silindi: {instance.title}",
        'calendar'
    )