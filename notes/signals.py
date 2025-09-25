from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Note
from dashboard.models import CalendarEvent
from user_profile.models import Notification
from django.urls import reverse
from django.db import transaction
from user_profile.tasks import send_notification, send_email_notification


@receiver(post_save, sender=Note)
def update_note_calendar_event(sender, instance, created, **kwargs):
    # Transaction'ı kaldır ve doğrudan işle
    try:
        # Önce mevcut etkinlikleri sil
        CalendarEvent.objects.filter(related_note=instance).delete()
        
        # İlişkili tarih varsa ve not kaydedilmişse yeni etkinlik oluştur
        if instance.related_date and instance.pk:
            CalendarEvent.objects.create(
                user=instance.user,
                title=f"Not: {instance.title}",
                start=instance.related_date,
                all_day=True,
                description=instance.content[:200],
                event_type='note',
                related_note=instance
            )
    except Exception as e:
        print(f"Takvim etkinliği güncelleme hatası: {e}")

@receiver(post_delete, sender=Note)
def delete_note_calendar_event(sender, instance, **kwargs):
    try:
        CalendarEvent.objects.filter(related_note=instance).delete()
    except Exception as e:
        print(f"CalendarEvent silme hatası: {e}")

@receiver(post_save, sender=Note)
def create_note_notification(sender, instance, created, **kwargs):
    if created:
        # Yeni not oluşturulduğunda
        message = f"Yeni not: {instance.title}"
        Notification.objects.create(
            user=instance.user,
            message=message,
            notification_type='note',
            related_id=instance.id,
            url=reverse('notes:note_detail', args=[instance.id])
        )
    elif not created:
        # Not güncellendiğinde
        message = f"'{instance.title}' notu güncellendi."
        Notification.objects.create(
            user=instance.user,
            message=message,
            notification_type='note',
            related_id=instance.id,
            url=reverse('notes:note_detail', args=[instance.id])
        )

@receiver(post_delete, sender=Note)
def delete_note_notification(sender, instance, **kwargs):
    try:
        message = f"'{instance.title}' notu silindi."
        Notification.objects.create(
            user=instance.user,
            message=message,
            notification_type='note'
        )
    except Exception as e:
        print(f"Bildirim oluşturma hatası: {e}")

@receiver(post_save, sender=Note)
def handle_note_notifications(sender, instance, created, **kwargs):
    try:
        if created:
            message = f"Yeni not: {instance.title}"
        else:
            message = f"'{instance.title}' notu güncellendi"
            
        Notification.objects.create(
            user=instance.user,
            message=message,
            notification_type='note',
            related_id=instance.id,
            url=reverse('notes:note_detail', args=[instance.id])
        )
    except Exception as e:
        print(f"Bildirim oluşturulamadı: {e}")

@receiver(post_delete, sender=Note)
def handle_note_deletion(sender, instance, **kwargs):
    try:
        Notification.objects.create(
            user=instance.user,
            message=f"'{instance.title}' notu silindi",
            notification_type='note'
        )
    except Exception as e:
        print(f"Silme bildirimi oluşturulamadı: {e}")

@receiver(post_save, sender=Note)
def note_created_or_updated(sender, instance, created, **kwargs):
    if created:
        send_notification.delay(
            instance.user.id,
            f"Yeni not: {instance.title}",
            'note',
            instance.id
        )
        
        if instance.user.profile.email_notifications:
            send_email_notification.delay(
                instance.user.id,
                "Yeni Not Oluşturuldu",
                f"'{instance.title}' adlı yeni bir not oluşturdunuz."
            )
    else:
        send_notification.delay(
            instance.user.id,
            f"Not güncellendi: {instance.title}",
            'note',
            instance.id
        )

@receiver(post_delete, sender=Note)
def note_deleted(sender, instance, **kwargs):
    send_notification.delay(
        instance.user.id,
        f"Not silindi: {instance.title}",
        'note'
    )