from celery import shared_task
from .models import CalendarEvent
from user_profile.tasks import send_notification, send_email_notification
from django.utils import timezone

@shared_task
def schedule_event_reminder(event_id):
    try:
        event = CalendarEvent.objects.get(id=event_id)
        
        # Hatırlatıcıyı gönder
        send_notification.delay(
            event.user.id,
            f"Etkinlik hatırlatıcı: {event.title} başlamak üzere!",
            'calendar',
            event.id,
            event.get_absolute_url()
        )
        
        # E-posta bildirimi
        if event.user.profile.email_notifications:
            send_email_notification.delay(
                event.user.id,
                "Etkinlik Hatırlatıcı",
                f"'{event.title}' etkinliği başlamak üzere!"
            )
        
        # Hatırlatıcının gönderildiğini işaretle
        event.reminder_sent = True
        event.save()
        
        return f"Etkinlik hatırlatıcısı gönderildi: {event.title}"
    
    except CalendarEvent.DoesNotExist:
        return "Etkinlik bulunamadı"