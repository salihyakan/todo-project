from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from .models import UserBadge, Badge, BadgeType
from todo.models import Task 
from notes.models import Note 
from dashboard.models import DashboardStats
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib import messages
from django.contrib.messages import get_messages
from django.db.models import Count
from .models import create_badge_types, create_badges


User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Kullanıcı yeni oluşturulduysa ve profil yoksa profil oluştur
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    # Kullanıcı kaydedildiğinde ilişkili profili de kaydet
    if hasattr(instance, 'profile'):
        instance.profile.save()

def award_badge(user, badge_slug, badge_data):
    badge, created = Badge.objects.get_or_create(
        slug=badge_slug,
        defaults=badge_data
    )
    # DÜZELTME: user_profile üzerinden oluşturma
    UserBadge.objects.get_or_create(
        user_profile=user.profile, 
        badge=badge
    )
    return badge, created

@receiver(post_save, sender=Task)
def check_task_completion_badges(sender, instance, created, **kwargs):
    if instance.status == 'completed' and not created:
        user = instance.user
        
        # Görev tamamlama sayısı
        completed_tasks = Task.objects.filter(user=user, status='completed').count()
        
        # Görev tamamlama rozetleri
        if completed_tasks >= 1:
            award_badge(user, 'first-task', {
                'name': 'İlk Adım',
                'description': 'İlk görevi tamamlama başarısı',
                'badge_type': BadgeType.objects.get_or_create(name='Görevler', defaults={
                    'description': 'Görev tamamlama rozetleri',
                    'icon': 'fas fa-tasks',
                    'color': '#3498db'
                })[0],
                'criteria': {'tasks_completed': 1}
            })
        
        if completed_tasks >= 10:
            award_badge(user, 'task-master', {
                'name': 'Görev Ustası',
                'description': '10 görev tamamlama başarısı',
                'badge_type': BadgeType.objects.get_or_create(name='Görevler', defaults={
                    'description': 'Görev tamamlama rozetleri',
                    'icon': 'fas fa-tasks',
                    'color': '#3498db'
                })[0],
                'criteria': {'tasks_completed': 10}
            })
        
        if completed_tasks >= 50:
            award_badge(user, 'task-expert', {
                'name': 'Görev Uzmanı',
                'description': '50 görev tamamlama başarısı',
                'badge_type': BadgeType.objects.get_or_create(name='Görevler', defaults={
                    'description': 'Görev tamamlama rozetleri',
                    'icon': 'fas fa-tasks',
                    'color': '#3498db'
                })[0],
                'criteria': {'tasks_completed': 50}
            })

@receiver(post_save, sender=Note)
def check_note_creation_badges(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        note_count = Note.objects.filter(user=user).count()
        
        # Not oluşturma rozetleri
        if note_count >= 5:
            award_badge(user, 'note-taker', {
                'name': 'Not Tutucu',
                'description': '5 not oluşturma başarısı',
                'badge_type': BadgeType.objects.get_or_create(name='Notlar', defaults={
                    'description': 'Not oluşturma rozetleri',
                    'icon': 'fas fa-sticky-note',
                    'color': '#f1c40f'
                })[0],
                'criteria': {'notes_created': 5}
            })
        
        if note_count >= 20:
            award_badge(user, 'note-expert', {
                'name': 'Not Uzmanı',
                'description': '20 not oluşturma başarısı',
                'badge_type': BadgeType.objects.get_or_create(name='Notlar', defaults={
                    'description': 'Not oluşturma rozetleri',
                    'icon': 'fas fa-sticky-note',
                    'color': '#f1c40f'
                })[0],
                'criteria': {'notes_created': 20}
            })

@receiver(post_save, sender=DashboardStats)
def check_streak_badges(sender, instance, created, **kwargs):
    user = instance.user
    
    # Giriş serisi rozetleri
    if instance.current_streak >= 3:
        award_badge(user, 'streak-beginner', {
            'name': 'Seri Başlangıcı',
            'description': '3 gün üst üste giriş yapma başarısı',
            'badge_type': BadgeType.objects.get_or_create(name='Seriler', defaults={
                'description': 'Giriş serisi rozetleri',
                'icon': 'fas fa-fire',
                'color': '#e74c3c'
            })[0],
            'criteria': {'login_streak': 3}
        })
    
    if instance.current_streak >= 7:
        award_badge(user, 'streak-master', {
            'name': 'Seri Ustası',
            'description': '7 gün üst üste giriş yapma başarısı',
            'badge_type': BadgeType.objects.get_or_create(name='Seriler', defaults={
                'description': 'Giriş serisi rozetleri',
                'icon': 'fas fa-fire',
                'color': '#e74c3c'
            })[0],
            'criteria': {'login_streak': 7}
        })
    
    if instance.current_streak >= 30:
        award_badge(user, 'streak-champion', {
            'name': 'Seri Şampiyonu',
            'description': '30 gün üst üste giriş yapma başarısı',
            'badge_type': BadgeType.objects.get_or_create(name='Seriler', defaults={
                'description': 'Giriş serisi rozetleri',
                'icon': 'fas fa-fire',
                'color': '#e74c3c'
            })[0],
            'criteria': {'login_streak': 30}
        })

# Pomodoro rozetleri
def check_pomodoro_badges(user, pomodoro_count):
    if pomodoro_count >= 10:
        award_badge(user, 'pomodoro-starter', {
            'name': 'Pomodoro Başlangıcı',
            'description': '10 Pomodoro seansı tamamlama başarısı',
            'badge_type': BadgeType.objects.get_or_create(name='Pomodoro', defaults={
                'description': 'Pomodoro seansı rozetleri',
                'icon': 'fas fa-clock',
                'color': '#9b59b6'
            })[0],
            'criteria': {'pomodoros_completed': 10}
        })
    
    if pomodoro_count >= 50:
        award_badge(user, 'pomodoro-master', {
            'name': 'Pomodoro Ustası',
            'description': '50 Pomodoro seansı tamamlama başarısı',
            'badge_type': BadgeType.objects.get_or_create(name='Pomodoro', defaults={
                'description': 'Pomodoro seansı rozetleri',
                'icon': 'fas fa-clock',
                'color': '#9b59b6'
            })[0],
            'criteria': {'pomodoros_completed': 50}
        })
    
@receiver(post_migrate)
def initialize_badges(sender, **kwargs):
    if sender.name == 'user_profile':
        create_badge_types()
        create_badges()
