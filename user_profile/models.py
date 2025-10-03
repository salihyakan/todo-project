from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name="Hakkımda")
    badges = models.ManyToManyField(
        'Badge', 
        through='UserBadge',
        related_name='profiles'
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        default='profile_pics/default.png',
        verbose_name="Profil Resmi"
    )
    location = models.CharField(max_length=100, blank=True, verbose_name="Konum")
    birth_date = models.DateField(null=True, blank=True, verbose_name="Doğum Tarihi")
    website = models.URLField(max_length=200, blank=True, verbose_name="Website")

    pomodoro_duration = models.PositiveIntegerField(
        default=25,
        validators=[MinValueValidator(5), MaxValueValidator(60)],
        verbose_name="Pomodoro Süresi (dakika)"
    )
    daily_goal = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        verbose_name="Günlük Hedef (görev)"
    )
    email_notifications = models.BooleanField(
        default=True,
        verbose_name="E-posta Bildirimleri"
    )
    push_notifications = models.BooleanField(
        default=True,
        verbose_name="Anlık Bildirimler"
    )
    notification_sound = models.BooleanField(
        default=True,
        verbose_name="Bildirim Sesi"
    )
    
    # Rozet kontrolü için ek alanlar
    last_login_date = models.DateField(null=True, blank=True, verbose_name="Son Giriş Tarihi")
    login_streak = models.PositiveIntegerField(default=0, verbose_name="Giriş Serisi")
    total_pomodoro_minutes = models.PositiveIntegerField(default=0, verbose_name="Toplam Pomodoro Süresi (dakika)")
    last_pomodoro_date = models.DateField(null=True, blank=True, verbose_name="Son Pomodoro Tarihi")
    
    class Meta:
        indexes = [
            models.Index(fields=['user']),  # OneToOneField için index
            models.Index(fields=['slug']),  # Slug için index
            models.Index(fields=['login_streak']),  # Giriş serisi için index
        ]
    
    def __str__(self):
        return f"{self.user.username} Profili"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.user.username)
            slug = base_slug
            counter = 1
            while Profile.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
    
    def calculate_profile_completion(self):
        """Profil tamamlama yüzdesini hesapla"""
        fields_to_check = [
            self.bio,
            self.profile_picture,
            self.location, 
            self.birth_date,
            self.website,
        ]
        
        completed_fields = sum(1 for field in fields_to_check if field)
        total_fields = len(fields_to_check)
        
        return (completed_fields / total_fields) * 100 if total_fields > 0 else 0

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        # Yeni kullanıcıya "Hoş Geldin" rozetini ver
        try:
            welcome_badge = Badge.objects.get(name='Hoş Geldin')
            UserBadge.objects.create(user_profile=profile, badge=welcome_badge)
        except Badge.DoesNotExist:
            # Rozet henüz oluşturulmamışsa pas geç
            pass

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()

class BadgeType(models.Model):
    name = models.CharField(max_length=100, verbose_name="Rozet Tipi")
    description = models.TextField(verbose_name="Açıklama")
    color = models.CharField(
        max_length=7, 
        default='#6c757d',
        validators=[RegexValidator(regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')]
    )
    icon = models.CharField(
        max_length=50, 
        default='fas fa-medal'
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),  # İsim ile arama için index
        ]
        verbose_name = 'Rozet Tipi'
        verbose_name_plural = 'Rozet Tipleri'
    
    def __str__(self):
        return self.name

class Badge(models.Model):
    name = models.CharField(max_length=100, verbose_name="Rozet Adı")
    description = models.TextField(verbose_name="Açıklama")
    badge_type = models.ForeignKey(
        BadgeType, 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='badges'
    )
    criteria = models.JSONField(default=dict, help_text="Kazanma kriterleri (JSON formatında)")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    is_secret = models.BooleanField(default=False, verbose_name="Gizli Rozet")
    icon = models.CharField(
        max_length=50, 
        default='fas fa-medal'
    )
    color = models.CharField(
        max_length=7, 
        default='#6c757d',
        validators=[RegexValidator(regex='^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$')]
    )
    
    class Meta:
        indexes = [
            models.Index(fields=['name']),  # İsim ile arama için index
            models.Index(fields=['slug']),  # Slug ile arama için index
            models.Index(fields=['badge_type']),  # Badge type ile filtreleme için index
            models.Index(fields=['is_secret']),  # Gizli rozetler için index
        ]
        verbose_name = 'Rozet'
        verbose_name_plural = 'Rozetler'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Badge.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
        
    def get_criteria_display(self):
        """Kriterleri kullanıcı dostu formatta göster"""
        criteria_list = []
        for key, value in self.criteria.items():
            # Kriter anahtarlarını Türkçe'ye çevir
            key_mapping = {
                'completed_tasks': 'Tamamlanan Görev',
                'quick_completion': 'Hızlı Tamamlama',
                'early_completion': 'Erken Tamamlama',
                'note_count': 'Not Sayısı',
                'category_count': 'Kategori Sayısı',
                'total_pomodoro_time': 'Toplam Pomodoro Süresi (dakika)',
                'consecutive_days': 'Ardışık Gün',
                'login_streak': 'Giriş Serisi',
                'profile_completion': 'Profil Tamamlama (%)',
                'morning_login': 'Sabah Girişi',
                'night_login': 'Gece Girişi',
                'weekend_login': 'Hafta Sonu Girişi',
                'perfect_day': 'Mükemmel Gün',
                'perfect_week': 'Mükemmel Hafta',
                'different_days': 'Farklı Gün',
                'all_badges': 'Tüm Rozetler'
            }
            
            display_key = key_mapping.get(key, key.replace('_', ' ').title())
            criteria_list.append(f"{display_key}: {value}")
        
        return criteria_list

class UserBadge(models.Model):
    user_profile = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,
        related_name='user_badges'
    )
    badge = models.ForeignKey(
        Badge, 
        on_delete=models.CASCADE,
        related_name='user_badges'
    )
    awarded_at = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False, verbose_name="Görüldü mü?")
    
    class Meta:
        unique_together = ('user_profile', 'badge')
        ordering = ['-awarded_at']
        indexes = [
            models.Index(fields=['user_profile', 'awarded_at']),  # Kullanıcı ve tarih için composite index
            models.Index(fields=['awarded_at']),  # Tarih sıralama için index
            models.Index(fields=['is_seen']),  # Görülmemiş rozetler için index
            models.Index(fields=['user_profile', 'is_seen']),  # Kullanıcıya özel görülmemiş rozetler için index
        ]
        verbose_name = 'Kullanıcı Rozeti'
        verbose_name_plural = 'Kullanıcı Rozetleri'
    
    def __str__(self):
        return f"{self.user_profile.user.username} - {self.badge.name}"
    
    def mark_as_seen(self):
        if not self.is_seen:
            self.is_seen = True
            self.save()
    
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('task', 'Görev'),
        ('note', 'Not'),
        ('system', 'Sistem'),
        ('achievement', 'Başarı'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    related_id = models.PositiveIntegerField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    url = models.URLField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),  # Kullanıcı ve tarih için composite index
            models.Index(fields=['user', 'is_read']),  # Okunmamış bildirimler için index
            models.Index(fields=['created_at']),  # Tarih sıralama için index
            models.Index(fields=['is_read']),  # Okunma durumu için index
            models.Index(fields=['notification_type']),  # Bildirim tipi için index
        ]
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"


def create_badge_types():
    """Rozet tiplerini oluştur"""
    if BadgeType.objects.count() == 0:
        types = [
            {
                'name': 'Görev Tamamlama',
                'description': 'Görevlerinizi tamamlayarak kazanabileceğiniz rozetler',
                'icon': 'fas fa-tasks',
                'color': '#3498db'
            },
            {
                'name': 'Not Oluşturma',
                'description': 'Notlar oluşturarak bilgi birikiminizi artırın',
                'icon': 'fas fa-sticky-note',
                'color': '#f1c40f'
            },
            {
                'name': 'Pomodoro Seansları',
                'description': 'Odaklanma seanslarınızla verimliliğinizi kanıtlayın',
                'icon': 'fas fa-clock',
                'color': '#9b59b6'
            },
            {
                'name': 'Giriş Serileri',
                'description': 'Düzenli kullanım alışkanlıklarınızı ödüllendirir',
                'icon': 'fas fa-fire',
                'color': '#e74c3c'
            },
            {
                'name': 'Çeşitli Başarılar',
                'description': 'Farklı aktivitelerle kazanılan özel rozetler',
                'icon': 'fas fa-star',
                'color': '#2ecc71'
            },
        ]
        
        for type_data in types:
            BadgeType.objects.get_or_create(**type_data)

def create_badges():
    """Rozetleri oluştur"""
    create_badge_types()
    
    if Badge.objects.count() == 0:
        # Görev rozetleri - her biri farklı icon
        task_badges = [
            {'name': 'İlk Görev', 'description': 'İlk görevi tamamla', 'criteria': {'completed_tasks': 1}, 'icon': 'fas fa-flag-checkered'},
            {'name': 'Görev Ustası', 'description': '10 görev tamamla', 'criteria': {'completed_tasks': 10}, 'icon': 'fas fa-tasks'},
            {'name': 'Görev Efendisi', 'description': '50 görev tamamla', 'criteria': {'completed_tasks': 50}, 'icon': 'fas fa-crown'},
            {'name': 'Görev Kralı', 'description': '100 görev tamamla', 'criteria': {'completed_tasks': 100}, 'icon': 'fas fa-chess-king'},
            {'name': 'Hızlı Başlangıç', 'description': 'Bir görevi oluşturulduktan 1 saat içinde tamamla', 'criteria': {'quick_completion': 1}, 'icon': 'fas fa-bolt'},
            {'name': 'Zaman Yönetimi', 'description': 'Son güne kalmadan 10 görev tamamla', 'criteria': {'early_completion': 10}, 'icon': 'fas fa-clock'},
            {'name': 'Hızlı Tamamlayıcı', 'description': 'Bir görevi oluşturulduktan 10 dakika içinde tamamla', 'criteria': {'quick_completion': 1}, 'icon': 'fas fa-running'},
        ]
        
        # Not rozetleri
        note_badges = [
            {'name': 'İlk Not', 'description': 'İlk notu oluştur', 'criteria': {'note_count': 1}, 'icon': 'fas fa-sticky-note'},
            {'name': 'Not Tutucu', 'description': '5 not oluştur', 'criteria': {'note_count': 5}, 'icon': 'fas fa-book'},
            {'name': 'Not Sever', 'description': '20 not oluştur', 'criteria': {'note_count': 20}, 'icon': 'fas fa-book-open'},
            {'name': 'Not Koleksiyoncusu', 'description': '50 not oluştur', 'criteria': {'note_count': 50}, 'icon': 'fas fa-archive'},
            {'name': 'Kategorize Edici', 'description': '5 farklı kategoride not oluştur', 'criteria': {'category_count': 5}, 'icon': 'fas fa-folder-tree'},
        ]
        
        # Pomodoro rozetleri
        pomodoro_badges = [
            {'name': 'Pomodoro Acemisi', 'description': 'Toplam 1 saat pomodoro yap', 'criteria': {'total_pomodoro_time': 60}, 'icon': 'fas fa-hourglass-start'},
            {'name': 'Pomodoro Sever', 'description': 'Toplam 5 saat pomodoro yap', 'criteria': {'total_pomodoro_time': 300}, 'icon': 'fas fa-hourglass-half'},
            {'name': 'Pomodoro Ustası', 'description': 'Toplam 25 saat pomodoro yap', 'criteria': {'total_pomodoro_time': 1500}, 'icon': 'fas fa-hourglass-end'},
            {'name': 'Pomodoro Maratoncusu', 'description': 'Tek seferde 10 pomodoro tamamla', 'criteria': {'consecutive_days': 3}, 'icon': 'fas fa-infinity'},
            {'name': 'Aralıksız Çalışma', 'description': '3 gün üst üste pomodoro yap', 'criteria': {'consecutive_days': 3}, 'icon': 'fas fa-fire'},
        ]
        
        # Seri rozetleri
        streak_badges = [
            {'name': 'İlk Giriş', 'description': 'İlk giriş yap', 'criteria': {'login_streak': 1}, 'icon': 'fas fa-door-open'},
            {'name': 'Düzenli Kullanıcı', 'description': '3 gün üst üste giriş yap', 'criteria': {'login_streak': 3}, 'icon': 'fas fa-calendar-day'},
            {'name': 'Sadık Kullanıcı', 'description': '7 gün üst üste giriş yap', 'criteria': {'login_streak': 7}, 'icon': 'fas fa-calendar-week'},
            {'name': 'Tam Bağımlı', 'description': '30 gün üst üste giriş yap', 'criteria': {'login_streak': 30}, 'icon': 'fas fa-calendar-alt'},
            {'name': 'Efsanevi Seri', 'description': '100 gün üst üste giriş yap', 'criteria': {'login_streak': 100}, 'icon': 'fas fa-award'},
        ]
        
        # Çeşitli rozetler
        misc_badges = [
            {'name': 'Profil Tamamlama', 'description': 'Profili %80 tamamla', 'criteria': {'profile_completion': 80}, 'icon': 'fas fa-user-check'},
            {'name': 'Erken Kuş', 'description': 'Sabah 6-8 arasında giriş yap', 'criteria': {'morning_login': 1}, 'icon': 'fas fa-sun'},
            {'name': 'Gece Kuşu', 'description': 'Gece 12-2 arasında giriş yap', 'criteria': {'night_login': 1}, 'icon': 'fas fa-moon'},
            {'name': 'Hafta Sonu', 'description': 'Hafta sonu giriş yap', 'criteria': {'weekend_login': 1}, 'icon': 'fas fa-umbrella-beach'},
            {'name': 'Mükemmel Gün', 'description': 'Bir günde tüm görevleri tamamla', 'criteria': {'perfect_day': 1}, 'icon': 'fas fa-star'},
            {'name': 'Tamamlanmış Hafta', 'description': 'Bir hafta boyunca tüm görevleri tamamla', 'criteria': {'perfect_week': 1}, 'icon': 'fas fa-trophy'},
            {'name': 'Yıldız Kullanıcı', 'description': '10 farklı günde giriş yap', 'criteria': {'different_days': 10}, 'icon': 'fas fa-user-astronaut'},
            {'name': 'Efsanevi Kullanıcı', 'description': 'Tüm rozetleri kazan', 'criteria': {'all_badges': 1}, 'icon': 'fas fa-robot'},
            {'name': 'Hoş Geldin', 'description': 'Hesap oluşturma başarısı', 'criteria': {}, 'icon': 'fas fa-handshake'},
        ]
        
        # Tüm rozetleri birleştir
        all_badges = [
            (BadgeType.objects.get(name='Görev Tamamlama'), task_badges),
            (BadgeType.objects.get(name='Not Oluşturma'), note_badges),
            (BadgeType.objects.get(name='Pomodoro Seansları'), pomodoro_badges),
            (BadgeType.objects.get(name='Giriş Serileri'), streak_badges),
            (BadgeType.objects.get(name='Çeşitli Başarılar'), misc_badges),
        ]
        
        # Rozetleri oluştur
        for badge_type, badges in all_badges:
            for badge_data in badges:
                Badge.objects.get_or_create(
                    name=badge_data['name'],
                    defaults={
                        'description': badge_data['description'],
                        'badge_type': badge_type,
                        'criteria': badge_data['criteria'],
                        'icon': badge_data['icon'],  # Burada her rozetin kendi iconu
                        'color': badge_type.color
                    }
                )

@receiver(post_migrate)
def initialize_badges(sender, **kwargs):
    """Migration sonrası rozetleri oluştur"""
    if sender.name == 'user_profile':
        create_badge_types()
        create_badges()