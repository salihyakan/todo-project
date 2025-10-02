from django.utils import timezone
from datetime import timedelta
from .models import UserBadge, Badge, Profile, Notification
from todo.models import Task
from notes.models import Note
from django.db.models import Count, Q
import logging

logger = logging.getLogger(__name__)

class BadgeChecker:
    def __init__(self, profile):
        self.profile = profile
        self.user = profile.user
    
    def check_and_award_badges(self):
        """Tüm rozet kriterlerini kontrol et ve uygun olanları ver"""
        self.check_task_badges()
        self.check_note_badges()
        self.check_pomodoro_badges()
        self.check_streak_badges()
        self.check_misc_badges()
    
    def check_task_badges(self):
        """Görev tamamlama rozetlerini kontrol et"""
        try:
            # Status'u 'completed' olan görevleri say
            completed_tasks = Task.objects.filter(
                user=self.user, 
                status='completed'
            ).count()
            
            # Hızlı tamamlama kontrolü (1 saat içinde)
            one_hour_ago = timezone.now() - timedelta(hours=1)
            quick_completions = Task.objects.filter(
                user=self.user,
                status='completed',
                updated_at__gte=one_hour_ago
            ).count()
            
            # Erken tamamlama kontrolü (son güne kalmadan)
            early_completions = Task.objects.filter(
                user=self.user,
                status='completed',
                due_date__isnull=False
            ).filter(
                updated_at__lt=timezone.now() - timedelta(days=1)
            ).count()
            
            # Mükemmel gün kontrolü (bir günde tüm görevlerin tamamlanması)
            today = timezone.now().date()
            today_tasks = Task.objects.filter(
                user=self.user,
                updated_at__date=today,
                status='completed'
            )
            total_today_tasks = Task.objects.filter(
                user=self.user,
                created_at__date=today
            ).count()
            perfect_day = total_today_tasks > 0 and today_tasks.count() == total_today_tasks
            
            # Rozet kontrolleri
            badges_to_check = [
                ('İlk Görev', completed_tasks >= 1),
                ('Görev Ustası', completed_tasks >= 10),
                ('Görev Efendisi', completed_tasks >= 50),
                ('Görev Kralı', completed_tasks >= 100),
                ('Hızlı Başlangıç', quick_completions >= 1),
                ('Zaman Yönetimi', early_completions >= 10),
                ('Hızlı Tamamlayıcı', quick_completions >= 1),
                ('Mükemmel Gün', perfect_day),
            ]
            
            for badge_name, condition in badges_to_check:
                if condition:
                    self.award_badge(badge_name)
                    
        except Exception as e:
            logger.error(f"Görev rozetleri kontrol edilirken hata: {e}")
    
    def check_note_badges(self):
        """Not oluşturma rozetlerini kontrol et"""
        try:
            # Toplam not sayısı
            note_count = Note.objects.filter(user=self.user).count()
            
            # Farklı kategori sayısı
            category_count = Note.objects.filter(
                user=self.user
            ).values('category').distinct().count()
            
            badges_to_check = [
                ('İlk Not', note_count >= 1),
                ('Not Tutucu', note_count >= 5),
                ('Not Sever', note_count >= 20),
                ('Not Koleksiyoncusu', note_count >= 50),
                ('Kategorize Edici', category_count >= 5),
            ]
            
            for badge_name, condition in badges_to_check:
                if condition:
                    self.award_badge(badge_name)
                    
        except Exception as e:
            logger.error(f"Not rozetleri kontrol edilirken hata: {e}")
    
    def check_pomodoro_badges(self):
        """Pomodoro rozetlerini kontrol et"""
        try:
            total_pomodoro_time = self.profile.total_pomodoro_minutes or 0
            
            # Pomodoro serisi kontrolü
            today = timezone.now().date()
            consecutive_days = 0
            
            if self.profile.last_pomodoro_date:
                last_pomodoro = self.profile.last_pomodoro_date
                if last_pomodoro == today:
                    consecutive_days = self.get_pomodoro_streak()
            
            badges_to_check = [
                ('Pomodoro Acemisi', total_pomodoro_time >= 60),
                ('Pomodoro Sever', total_pomodoro_time >= 300),
                ('Pomodoro Ustası', total_pomodoro_time >= 1500),
                ('Aralıksız Çalışma', consecutive_days >= 3),
            ]
            
            for badge_name, condition in badges_to_check:
                if condition:
                    self.award_badge(badge_name)
                    
        except Exception as e:
            logger.error(f"Pomodoro rozetleri kontrol edilirken hata: {e}")
    
    def get_pomodoro_streak(self):
        """Pomodoro serisini hesapla"""
        # Basit bir implementasyon - gerçek uygulamada daha detaylı olmalı
        return self.profile.login_streak  # Şimdilik giriş serisini kullan
    
    def check_streak_badges(self):
        """Giriş serisi rozetlerini kontrol et"""
        try:
            login_streak = self.profile.login_streak or 0
            
            badges_to_check = [
                ('İlk Giriş', True),  # Her kullanıcıya verilir
                ('Düzenli Kullanıcı', login_streak >= 3),
                ('Sadık Kullanıcı', login_streak >= 7),
                ('Tam Bağımlı', login_streak >= 30),
                ('Efsanevi Seri', login_streak >= 100),
            ]
            
            for badge_name, condition in badges_to_check:
                if condition:
                    self.award_badge(badge_name)
                    
        except Exception as e:
            logger.error(f"Seri rozetleri kontrol edilirken hata: {e}")
    
    def check_misc_badges(self):
        """Çeşitli rozetleri kontrol et"""
        try:
            # Profil tamamlama kontrolü
            profile_completion = self.profile.calculate_profile_completion()
            
            # Zaman bazlı kontroller
            now = timezone.now()
            is_morning = 6 <= now.hour <= 8
            is_night = 0 <= now.hour <= 2 or 22 <= now.hour <= 23
            is_weekend = now.weekday() >= 5  # 5=Cumartesi, 6=Pazar
            
            # Tüm rozetleri kazanma kontrolü
            total_badges = Badge.objects.count()
            earned_badges = UserBadge.objects.filter(user_profile=self.profile).count()
            all_badges_earned = total_badges > 0 and earned_badges == total_badges
            
            # Farklı gün sayısı (basit implementasyon)
            different_days = self.profile.login_streak if self.profile.login_streak <= 10 else 10
            
            badges_to_check = [
                ('Profil Tamamlama', profile_completion >= 80),
                ('Erken Kuş', is_morning),
                ('Gece Kuşu', is_night),
                ('Hafta Sonu', is_weekend),
                ('Yıldız Kullanıcı', different_days >= 10),
                ('Efsanevi Kullanıcı', all_badges_earned),
                ('Hoş Geldin', True),  # Yeni kullanıcılar için
            ]
            
            for badge_name, condition in badges_to_check:
                if condition:
                    self.award_badge(badge_name)
                    
        except Exception as e:
            logger.error(f"Çeşitli rozetler kontrol edilirken hata: {e}")
    
    def award_badge(self, badge_name):
        """Rozeti kullanıcıya ver ve bildirim oluştur"""
        try:
            badge = Badge.objects.get(name=badge_name)
            
            # Rozet zaten verilmiş mi kontrol et
            if not UserBadge.objects.filter(
                user_profile=self.profile, 
                badge=badge
            ).exists():
                
                # Yeni rozet ver
                user_badge = UserBadge.objects.create(
                    user_profile=self.profile,
                    badge=badge
                )
                
                # Aynı bildirim daha önce oluşturulmuş mu kontrol et
                existing_notification = Notification.objects.filter(
                    user=self.user,
                    notification_type='achievement',
                    related_id=badge.id,
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).exists()
                
                if not existing_notification:
                    # Bildirim oluştur
                    Notification.objects.create(
                        user=self.user,
                        message=f'Tebrikler! "{badge.name}" rozetini kazandınız! 🎉',
                        notification_type='achievement',
                        related_id=badge.id,
                        url=f'/profile/badges/{badge.slug}/'
                    )
                
                logger.info(f"{self.user.username} kullanıcısına {badge_name} rozeti verildi")
                return True
                
        except Badge.DoesNotExist:
            logger.error(f"Rozet bulunamadı: {badge_name}")
        except Exception as e:
            logger.error(f"Rozet verilirken hata: {e}")
        
        return False

def check_user_badges(profile):
    """Kullanıcı rozetlerini kontrol etmek için ana fonksiyon"""
    checker = BadgeChecker(profile)
    checker.check_and_award_badges()