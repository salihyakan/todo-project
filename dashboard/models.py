from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
import pytz

User = get_user_model()

class DashboardStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    last_login = models.DateTimeField(auto_now=True)
    tasks_completed = models.PositiveIntegerField(default=0)
    pomodoros_completed = models.PositiveIntegerField(default=0)
    notes_created = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    
    def update_stats(self):
        # Geçici import kullanarak döngüsel import'u önle
        try:
            from todo.models import Task
            self.tasks_completed = Task.objects.filter(
                user=self.user, 
                status='completed'
            ).count()
            self.save()
        except ImportError:
            pass
    
    def __str__(self):
        return f"{self.user.username} İstatistikleri"

class CalendarEvent(models.Model):
    EVENT_TYPES = [
        ('reminder', 'Hatırlatıcı'),
        ('event', 'Etkinlik'),
        ('note', 'Not'),
        ('task', 'Görev')
    ]
    
    REMINDER_CHOICES = [
        (5, '5 dakika önce'),
        (15, '15 dakika önce'),
        (30, '30 dakika önce'),
        (60, '1 saat önce'),
        (1440, '1 gün önce'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    is_all_day = models.BooleanField(default=False)
    
    # String referans kullanarak döngüsel import'u önle
    related_note = models.ForeignKey('notes.Note', on_delete=models.CASCADE, null=True, blank=True)
    related_task = models.ForeignKey('todo.Task', on_delete=models.CASCADE, null=True, blank=True)
    
    reminder = models.PositiveIntegerField(
        choices=REMINDER_CHOICES, 
        null=True, 
        blank=True,
        verbose_name="Hatırlatıcı"
    )
    reminder_sent = models.BooleanField(default=False, verbose_name="Hatırlatıcı Gönderildi")
    
    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"
    
    def get_absolute_url(self):
        return reverse('dashboard:event_detail', args=[str(self.id)])
    
    @property
    def reminder_time(self):
        if self.reminder:
            # Mevcut zaman diliminde hesapla
            return self.start_date - timezone.timedelta(minutes=self.reminder)
        return None
    
    @property
    def color(self):
        colors = {
            'reminder': '#dc3545',  # Kırmızı
            'event': '#28a745',     # Yeşil
            'note': '#ffc107',      # Sarı
            'task': '#3788d8'       # Mavi
        }
        return colors.get(self.event_type, '#6c757d')