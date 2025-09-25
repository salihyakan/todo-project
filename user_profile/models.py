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

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = Profile.objects.create(user=instance)
        # Yeni kullanıcıya "Hoş Geldin" rozetini ver
        welcome_badge = Badge.objects.get(name='Hoş Geldin')
        UserBadge.objects.create(user_profile=profile, badge=welcome_badge)

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
        return [f"{key.replace('_', ' ').title()}: {value}" for key, value in self.criteria.items()]

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

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bildirim'
        verbose_name_plural = 'Bildirimler'


def create_badge_types():
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
    create_badge_types()
    
    if Badge.objects.count() == 0:
        # Görev rozetleri
        task_badges = [
            {'name': 'İlk Görev', 'description': 'İlk görevi tamamla', 'criteria': {'tam_görev': 1}},
            {'name': 'Görev Ustası', 'description': '10 görev tamamla', 'criteria': {'tam_görev': 10}},
            {'name': 'Görev Efendisi', 'description': '50 görev tamamla', 'criteria': {'tam_görev': 50}},
            {'name': 'Görev Kralı', 'description': '100 görev tamamla', 'criteria': {'tam_görev': 100}},
            {'name': 'Hızlı Başlangıç', 'description': 'Bir görevi oluşturulduktan 1 saat içinde tamamla', 'criteria': {'hızlı_tamam': 1}},
            {'name': 'Zaman Yönetimi', 'description': 'Son güne kalmadan 10 görev tamamla', 'criteria': {'erken_tamam': 10}},
        ]
        
        # Not rozetleri
        note_badges = [
            {'name': 'İlk Not', 'description': 'İlk notu oluştur', 'criteria': {'not_sayısı': 1}},
            {'name': 'Not Tutucu', 'description': '5 not oluştur', 'criteria': {'not_sayısı': 5}},
            {'name': 'Not Sever', 'description': '20 not oluştur', 'criteria': {'not_sayısı': 20}},
            {'name': 'Not Koleksiyoncusu', 'description': '50 not oluştur', 'criteria': {'not_sayısı': 50}},
            {'name': 'Kategorize Edici', 'description': '5 farklı kategoride not oluştur', 'criteria': {'kategori_sayısı': 5}},
        ]
        
        # Pomodoro rozetleri
        pomodoro_badges = [
            {'name': 'Pomodoro Acemisi', 'description': 'Toplam 1 saat pomodoro yap', 'criteria': {'toplam_süre': 60}},
            {'name': 'Pomodoro Sever', 'description': 'Toplam 5 saat pomodoro yap', 'criteria': {'toplam_süre': 300}},
            {'name': 'Pomodoro Ustası', 'description': 'Toplam 25 saat pomodoro yap', 'criteria': {'toplam_süre': 1500}},
            {'name': 'Pomodoro Maratoncusu', 'description': 'Tek seferde 10 pomodoro tamamla', 'criteria': {'tek_seferde': 10}},
            {'name': 'Aralıksız Çalışma', 'description': '3 gün üst üste pomodoro yap', 'criteria': {'gün_serisi': 3}},
        ]
        
        # Seri rozetleri
        streak_badges = [
            {'name': 'İlk Giriş', 'description': 'İlk giriş yap', 'criteria': {'giriş': 1}},
            {'name': 'Düzenli Kullanıcı', 'description': '3 gün üst üste giriş yap', 'criteria': {'giriş_serisi': 3}},
            {'name': 'Sadık Kullanıcı', 'description': '7 gün üst üste giriş yap', 'criteria': {'giriş_serisi': 7}},
            {'name': 'Tam Bağımlı', 'description': '30 gün üst üste giriş yap', 'criteria': {'giriş_serisi': 30}},
            {'name': 'Efsanevi Seri', 'description': '100 gün üst üste giriş yap', 'criteria': {'giriş_serisi': 100}},
        ]
        
        # Çeşitli rozetler
        misc_badges = [
            {'name': 'Profil Tamamlama', 'description': 'Profili %100 tamamla', 'criteria': {'profil_tamam': 100}},
            {'name': 'Erken Kuş', 'description': 'Sabah 6-8 arasında giriş yap', 'criteria': {'sabah_girişi': 1}},
            {'name': 'Gece Kuşu', 'description': 'Gece 12-2 arasında giriş yap', 'criteria': {'gece_girişi': 1}},
            {'name': 'Hafta Sonu', 'description': 'Hafta sonu giriş yap', 'criteria': {'hafta_sonu_girişi': 1}},
            {'name': 'Sosyal', 'description': 'Profilini sosyal medya ile bağla', 'criteria': {'sosyal_bağlantı': 1}},
            {'name': 'Tamamlanmış Hafta', 'description': 'Bir hafta boyunca tüm görevleri tamamla', 'criteria': {'tam_hafta': 1}},
            {'name': 'Hızlı Tamamlayıcı', 'description': 'Bir görevi oluşturulduktan 10 dakika içinde tamamla', 'criteria': {'süper_hızlı': 1}},
            {'name': 'Mükemmel Gün', 'description': 'Bir günde tüm görevleri tamamla', 'criteria': {'mükemmel_gün': 1}},
            {'name': 'Yıldız Kullanıcı', 'description': '10 farklı günde giriş yap', 'criteria': {'farklı_gün': 10}},
            {'name': 'Efsanevi Kullanıcı', 'description': 'Tüm rozetleri kazan', 'criteria': {'tüm_rozetler': 1}},
            {'name': 'Hoş Geldin', 'description': 'Hesap oluşturma başarısı', 'criteria': {}},
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
                        'icon': badge_type.icon,
                        'color': badge_type.color
                    }
                )

@receiver(post_migrate)
def initialize_badges(sender, **kwargs):
    if sender.name == 'user_profile':
        create_badge_types()
        create_badges()