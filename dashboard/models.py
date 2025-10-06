from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta, datetime
from todo.models import Task
from notes.models import Note


User = get_user_model()

class DashboardStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    tasks_completed = models.IntegerField(default=0)
    pomodoros_completed = models.IntegerField(default=0)
    notes_created = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'last_updated']),
            models.Index(fields=['current_streak']),  # Yeni index
            models.Index(fields=['last_updated']),  # Yeni index
        ]
        verbose_name_plural = "Dashboard İstatistikleri"

    # Mevcut metodlar aynı kalacak...
    def update_stats(self):
        print(f"Updating stats for user: {self.user.username}")
        
        # Not sayısını güncelle
        notes_count = Note.objects.filter(user=self.user).count()
        self.notes_created = notes_count
        
        # Tamamlanan görev sayısı
        completed_tasks_count = Task.objects.filter(user=self.user, status='completed').count()
        self.tasks_completed = completed_tasks_count
        
        # Pomodoro sayısı - SADECE çalışma oturumlarını say
        try:
            from dashboard.models import PomodoroSession
            pomodoro_count = PomodoroSession.objects.filter(
                user=self.user, 
                completed=True,
                session_type='work'  # Sadece çalışma oturumlarını say
            ).count()
            self.pomodoros_completed = pomodoro_count
        except Exception as e:
            print(f"Pomodoro error: {e}")
            self.pomodoros_completed = 0
        
        # YENİ SERİ HESAPLAMA MANTIĞI
        # 2 gün kuralı: 1 gün boşluk seriyi bozmaz, 2 gün boşluk seriyi sıfırlar
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        # Bugün işlem yapılmış mı kontrol et
        today_activity = self._check_daily_activity(current_date)
        
        if today_activity:
            streak = 1
            # Dünden başlayarak geriye doğru kontrol et
            for day_count in range(1, 365):  # Maksimum 1 yıl
                check_date = today - timedelta(days=day_count)
                has_activity = self._check_daily_activity(check_date)
                
                if has_activity:
                    streak += 1
                else:
                    # Bir gün boşluk bulduk, bir gün daha kontrol et
                    if day_count + 1 < 365:
                        next_check_date = today - timedelta(days=day_count + 1)
                        next_has_activity = self._check_daily_activity(next_check_date)
                        
                        if next_has_activity:
                            # İkinci gün de aktivite varsa devam et
                            streak += 1
                            day_count += 1  # Bir gün daha atla
                        else:
                            # İki gün üst üste aktivite yok, seriyi bitir
                            break
                    else:
                        break
        else:
            # Bugün aktivite yok, dün kontrol et
            yesterday = today - timedelta(days=1)
            yesterday_activity = self._check_daily_activity(yesterday)
            
            if yesterday_activity:
                streak = 1
                # Dünden geriye doğru kontrol et
                for day_count in range(2, 365):
                    check_date = today - timedelta(days=day_count)
                    has_activity = self._check_daily_activity(check_date)
                    
                    if has_activity:
                        streak += 1
                    else:
                        # Bir gün boşluk bulduk, bir gün daha kontrol et
                        if day_count + 1 < 365:
                            next_check_date = today - timedelta(days=day_count + 1)
                            next_has_activity = self._check_daily_activity(next_check_date)
                            
                            if next_has_activity:
                                streak += 1
                                day_count += 1
                            else:
                                break
                        else:
                            break
        
        self.current_streak = streak
        self.save()
        print(f"Updated streak: {streak} days")

    def _check_daily_activity(self, date):
        """Belirli bir tarihte kullanıcının işlem yapıp yapmadığını kontrol et - Optimize edilmiş"""
        from todo.models import Task
        from notes.models import Note
        
        # Tarih aralığını belirle (o günün başından sonuna kadar)
        start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        
        print(f"Checking activity for {date}: {start_of_day} to {end_of_day}")
        
        # Görev tamamlandı mı?
        tasks_completed = Task.objects.filter(
            user=self.user,
            status='completed',
            completed_at__range=(start_of_day, end_of_day)
        ).exists()
        
        if tasks_completed:
            print(f"✓ Task completed on {date}")
            return True
        
        # Not oluşturuldu mu?
        notes_created = Note.objects.filter(
            user=self.user,
            created_at__range=(start_of_day, end_of_day)
        ).exists()
        
        if notes_created:
            print(f"✓ Note created on {date}")
            return True
        
        # Pomodoro tamamlandı mı?
        try:
            from dashboard.models import PomodoroSession
            pomodoro_completed = PomodoroSession.objects.filter(
                user=self.user,
                completed=True,
                created_at__range=(start_of_day, end_of_day)
            ).exists()
            
            if pomodoro_completed:
                print(f"✓ Pomodoro completed on {date}")
                return True
        except Exception as e:
            print(f"Pomodoro check error: {e}")
        
        print(f"✗ No activity found on {date}")
        return False

    def __str__(self):
        return f"{self.user.username} - Dashboard Stats"

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
    
    related_note = models.ForeignKey('notes.Note', on_delete=models.CASCADE, null=True, blank=True)
    related_task = models.ForeignKey('todo.Task', on_delete=models.CASCADE, null=True, blank=True)
    
    reminder = models.PositiveIntegerField(
        choices=REMINDER_CHOICES, 
        null=True, 
        blank=True,
        verbose_name="Hatırlatıcı"
    )
    reminder_sent = models.BooleanField(default=False, verbose_name="Hatırlatıcı Gönderildi")
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'start_date']),  # Yeni index
            models.Index(fields=['start_date', 'end_date']),  # Yeni index
            models.Index(fields=['event_type']),  # Yeni index
            models.Index(fields=['user', 'event_type', 'start_date']),  # Composite index
        ]
        ordering = ['-start_date']

    # Mevcut property ve metodlar aynı kalacak...
    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"
    
    def get_absolute_url(self):
        return reverse('dashboard:event_detail', args=[str(self.id)])
    
    @property
    def reminder_time(self):
        if self.reminder:
            return self.start_date - timezone.timedelta(minutes=self.reminder)
        return None
    
    @property
    def color(self):
        colors = {
            'reminder': '#dc3545',
            'event': '#28a745',
            'note': '#ffc107',
            'task': '#3788d8'
        }
        return colors.get(self.event_type, '#6c757d')
    
    def get_reminder_display(self):
        reminder_mapping = {
            5: '5 dakika',
            15: '15 dakika', 
            30: '30 dakika',
            60: '1 saat',
            1440: '1 gün'
        }
        return reminder_mapping.get(self.reminder, '')
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError('Bitiş tarihi başlangıç tarihinden önce olamaz.')
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class PomodoroSession(models.Model):
    SESSION_TYPES = [
        ('work', 'Çalışma'),
        ('break', 'Mola'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pomodoro_sessions')
    session_type = models.CharField(max_length=10, choices=SESSION_TYPES, default='work')
    duration = models.IntegerField(default=25, help_text="Dakika cinsinden")
    completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),  # Yeni index
            models.Index(fields=['session_type']),  # Yeni index
            models.Index(fields=['completed']),  # Yeni index
            models.Index(fields=['user', 'session_type', 'created_at']),  # Composite index
        ]
        verbose_name = 'Pomodoro Oturumu'
        verbose_name_plural = 'Pomodoro Oturumları'

    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()} - {self.duration}dk"