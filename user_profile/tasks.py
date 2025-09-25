from celery import shared_task
from django.contrib.auth import get_user_model
from .models import Notification
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

User = get_user_model()

@shared_task
def send_notification(user_id, message, notification_type='system', related_id=None, url=None):
    try:
        user = User.objects.get(id=user_id)
        # URL oluşturma
        if not url and related_id:
            if notification_type == 'task':
                url = reverse('todo:task_detail', args=[related_id])
            elif notification_type == 'note':
                url = reverse('notes:note_detail', args=[related_id])
            elif notification_type == 'calendar':
                url = reverse('dashboard:event_detail', args=[related_id])
        
        Notification.objects.create(
            user=user,
            message=message,
            notification_type=notification_type,
            related_id=related_id,
            url=url
        )
        return f"Bildirim gönderildi: {user.username}"
    except User.DoesNotExist:
        return "Kullanıcı bulunamadı"

@shared_task
def send_email_notification(user_id, subject, message):
    try:
        user = User.objects.get(id=user_id)
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return f"E-posta gönderildi: {user.email}"
    except User.DoesNotExist:
        return "Kullanıcı bulunamadı"