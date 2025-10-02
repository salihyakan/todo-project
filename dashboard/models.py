from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta, datetime

User = get_user_model()

class DashboardStats(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='dashboard_stats')
    tasks_completed = models.IntegerField(default=0)
    pomodoros_completed = models.IntegerField(default=0)
    notes_created = models.IntegerField(default=0)
    current_streak = models.IntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def update_stats(self):
        from todo.models import Task
        from notes.models import Note
        
        print(f"Updating stats for user: {self.user.username}")  # DEBUG
        
        # Not sayısını güncelle
        notes_count = Note.objects.filter(user=self.user).count()
        self.notes_created = notes_count
        print(f"Notes count: {notes_count}")  # DEBUG
        
        # Tamamlanan görev sayısı
        completed_tasks_count = Task.objects.filter(user=self.user, status='completed').count()
        self.tasks_completed = completed_tasks_count
        print(f"Completed tasks: {completed_tasks_count}")  # DEBUG
        
        # Pomodoro sayısı
        try:
            from tools.models import PomodoroSession
            pomodoro_count = PomodoroSession.objects.filter(user=self.user, completed=True).count()
            self.pomodoros_completed = pomodoro_count
            print(f"Pomodoro sessions: {pomodoro_count}")  # DEBUG
        except Exception as e:
            print(f"Pomodoro error: {e}")  # DEBUG
            self.pomodoros_completed = 0
        
        # GÜNLÜK SERİ HESAPLAMA - Basitleştirilmiş ve Debug Edilmiş
        today = timezone.now().date()
        streak = 0
        current_date = today
        
        print(f"Calculating streak for {self.user.username}")  # DEBUG
        
        # Bugün işlem yapılmış mı kontrol et
        today_activity = self._check_daily_activity(current_date)
        print(f"Today activity: {today_activity}")  # DEBUG
        
        # Dünden başlayarak geriye doğru kontrol et
        day_count = 0
        while day_count < 365:  # Maksimum 1 yıl
            check_date = today - timedelta(days=day_count)
            has_activity = self._check_daily_activity(check_date)
            print(f"Date: {check_date}, Activity: {has_activity}")  # DEBUG
            
            if has_activity:
                streak += 1
                day_count += 1
            else:
                break
        
        self.current_streak = streak
        print(f"Final streak: {streak}")  # DEBUG
        
        self.save()
        print(f"Stats saved: tasks={self.tasks_completed}, notes={self.notes_created}, streak={self.current_streak}")  # DEBUG

    def _check_daily_activity(self, date):
        """Belirli bir tarihte kullanıcının işlem yapıp yapmadığını kontrol et"""
        from todo.models import Task
        from notes.models import Note
        
        # Tarih aralığını belirle (o günün başından sonuna kadar)
        start_of_day = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_of_day = timezone.make_aware(datetime.combine(date, datetime.max.time()))
        
        # Görev tamamlandı mı?
        tasks_completed = Task.objects.filter(
            user=self.user,
            status='completed',
            completed_at__range=(start_of_day, end_of_day)
        ).exists()
        
        # Not oluşturuldu mu?
        notes_created = Note.objects.filter(
            user=self.user,
            created_at__range=(start_of_day, end_of_day)
        ).exists()
        
        # Pomodoro tamamlandı mı?
        pomodoro_completed = False
        try:
            from tools.models import PomodoroSession
            pomodoro_completed = PomodoroSession.objects.filter(
                user=self.user,
                completed=True,
                created_at__range=(start_of_day, end_of_day)
            ).exists()
        except:
            pass
        
        # Herhangi bir işlem varsa True döndür
        activity_found = tasks_completed or notes_created or pomodoro_completed
        
        # DEBUG: Hangi aktiviteler bulundu
        if activity_found:
            print(f"Activity found on {date}: tasks={tasks_completed}, notes={notes_created}, pomodoro={pomodoro_completed}")
        
        return activity_found

    def __str__(self):
        return f"{self.user.username} - Dashboard Stats"

    class Meta:
        verbose_name_plural = "Dashboard İstatistikleri"

# CalendarEvent modeli aynı kalabilir, sadece gerekli kısımları ekliyorum
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

    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()} - {self.duration}dk"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Pomodoro Oturumu'
        verbose_name_plural = 'Pomodoro Oturumları'