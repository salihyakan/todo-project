from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from todo.models import Task
from dashboard.models import CalendarEvent
from .models import Profile, Notification
from .utils import check_user_badges
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def check_task_badges_and_notifications(sender, instance, created, **kwargs):
    """Görev kaydedildiğinde rozetleri kontrol et ve bildirim oluştur"""
    try:
        profile = Profile.objects.get(user=instance.user)
        
        # Sadece tamamlanan görevler için rozet kontrolü
        if instance.status == 'completed':
            check_user_badges(profile)
            
        # Görev zamanı yaklaştığında bildirim oluştur (1 saat kala)
        check_task_reminder(instance)
            
    except Profile.DoesNotExist:
        pass

def check_task_reminder(task):
    """Görev zamanı yaklaştığında bildirim oluştur"""
    try:
        now = timezone.now()
        time_until_due = task.due_date - now
        
        # 1 saat içinde bitecek görevler için bildirim
        if timedelta(hours=0) < time_until_due <= timedelta(hours=1):
            # Aynı bildirim daha önce oluşturulmuş mu kontrol et
            existing_notification = Notification.objects.filter(
                user=task.user,
                notification_type='task',
                related_id=task.id,
                message__icontains=task.title,
                created_at__gte=now - timedelta(hours=1)
            ).exists()
            
            if not existing_notification:
                Notification.objects.create(
                    user=task.user,
                    message=f'"{task.title}" görevinin süresi 1 saat içinde doluyor! ⏰',
                    notification_type='task',
                    related_id=task.id,
                    url=f'/todo/tasks/{task.id}/'
                )
                logger.info(f"Görev bildirimi oluşturuldu: {task.title}")
                
    except Exception as e:
        logger.error(f"Görev bildirimi oluşturulurken hata: {e}")

@receiver(post_save, sender=CalendarEvent)
def check_calendar_event_reminders(sender, instance, created, **kwargs):
    """Takvim etkinliği kaydedildiğinde hatırlatıcıları kontrol et"""
    try:
        # Hatırlatıcı zamanı geldiyse bildirim oluştur
        check_calendar_reminder(instance)
    except Exception as e:
        logger.error(f"Takvim bildirimi oluşturulurken hata: {e}")

def check_calendar_reminder(event):
    """Takvim etkinliği hatırlatıcısı için bildirim oluştur"""
    try:
        now = timezone.now()
        
        if event.reminder and not event.reminder_sent:
            reminder_time = event.start_date - timedelta(minutes=event.reminder)
            
            # Hatırlatıcı zamanı geldi mi?
            if now >= reminder_time:
                # Aynı bildirim daha önce oluşturulmuş mu kontrol et
                existing_notification = Notification.objects.filter(
                    user=event.user,
                    notification_type='system',
                    related_id=event.id,
                    message__icontains=event.title,
                    created_at__gte=now - timedelta(hours=1)
                ).exists()
                
                if not existing_notification:
                    Notification.objects.create(
                        user=event.user,
                        message=f'"{event.title}" etkinliği {event.get_reminder_display()} başlıyor! 📅',
                        notification_type='system',
                        related_id=event.id,
                        url=event.get_absolute_url()
                    )
                    
                    # Hatırlatıcı gönderildi olarak işaretle
                    event.reminder_sent = True
                    event.save()
                    
                    logger.info(f"Takvim bildirimi oluşturuldu: {event.title}")
                    
    except Exception as e:
        logger.error(f"Takvim bildirimi oluşturulurken hata: {e}")

@receiver(user_logged_in)
def check_login_badges_and_reminders(sender, request, user, **kwargs):
    """Kullanıcı giriş yaptığında rozetleri ve hatırlatıcıları kontrol et"""
    try:
        profile = Profile.objects.get(user=user)
        
        # Giriş serisi kontrolü
        today = timezone.now().date()
        if profile.last_login_date:
            last_login = profile.last_login_date
            if last_login == today - timedelta(days=1):
                # Ardışık giriş
                profile.login_streak += 1
            elif last_login < today - timedelta(days=1):
                # Seri bozuldu
                profile.login_streak = 1
        else:
            # İlk giriş
            profile.login_streak = 1
        
        profile.last_login_date = today
        profile.save()
        
        # Rozet kontrolü
        check_user_badges(profile)
        
        # Yaklaşan görevler için bildirim kontrolü
        check_upcoming_tasks(user)
        
        # Yaklaşan takvim etkinlikleri için bildirim kontrolü
        check_upcoming_calendar_events(user)
        
    except Profile.DoesNotExist:
        pass

def check_upcoming_tasks(user):
    """Yaklaşan görevler için bildirim oluştur"""
    try:
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)
        
        # 1 saat içinde bitecek ve henüz tamamlanmamış görevler
        upcoming_tasks = Task.objects.filter(
            user=user,
            due_date__range=(now, one_hour_later),
            status__in=['todo', 'in_progress']
        ).exclude(
            # Daha önce bildirim oluşturulmuş görevleri hariç tut
            id__in=Notification.objects.filter(
                user=user,
                notification_type='task',
                created_at__gte=now - timedelta(hours=1)
            ).values_list('related_id', flat=True)
        )
        
        for task in upcoming_tasks:
            Notification.objects.create(
                user=user,
                message=f'"{task.title}" görevinin süresi 1 saat içinde doluyor! ⏰',
                notification_type='task',
                related_id=task.id,
                url=f'/todo/tasks/{task.id}/'
            )
            logger.info(f"Yaklaşan görev bildirimi oluşturuldu: {task.title}")
            
    except Exception as e:
        logger.error(f"Yaklaşan görev bildirimi oluşturulurken hata: {e}")

def check_upcoming_calendar_events(user):
    """Yaklaşan takvim etkinlikleri için bildirim oluştur"""
    try:
        now = timezone.now()
        one_hour_later = now + timedelta(hours=1)
        
        # 1 saat içinde başlayacak ve hatırlatıcısı gönderilmemiş etkinlikler
        upcoming_events = CalendarEvent.objects.filter(
            user=user,
            start_date__range=(now, one_hour_later),
            reminder_sent=False
        )
        
        for event in upcoming_events:
            # Aynı bildirim daha önce oluşturulmuş mu kontrol et
            existing_notification = Notification.objects.filter(
                user=user,
                notification_type='system',
                related_id=event.id,
                created_at__gte=now - timedelta(hours=1)
            ).exists()
            
            if not existing_notification:
                Notification.objects.create(
                    user=user,
                    message=f'"{event.title}" etkinliği yakında başlıyor! 📅',
                    notification_type='system',
                    related_id=event.id,
                    url=event.get_absolute_url()
                )
                
                # Hatırlatıcı gönderildi olarak işaretle
                event.reminder_sent = True
                event.save()
                
                logger.info(f"Yaklaşan etkinlik bildirimi oluşturuldu: {event.title}")
                
    except Exception as e:
        logger.error(f"Yaklaşan etkinlik bildirimi oluşturulurken hata: {e}")

@receiver(post_save, sender=Profile)
def check_profile_badges(sender, instance, created, **kwargs):
    """Profil güncellendiğinde rozetleri kontrol et"""
    if not created:  # Sadece güncellemelerde
        check_user_badges(instance)