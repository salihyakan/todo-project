import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from user_profile.models import Profile, Badge, BadgeType, Notification, UserBadge

User = get_user_model()

class UserProfileAuthenticationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile

    def test_user_login_success(self):
        """Başarılı login testi"""
        response = self.client.post(reverse('user_profile:login'), {
            'username': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_user_login_failure(self):
        """Başarısız login testi"""
        response = self.client.post(reverse('user_profile:login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Geçersiz')

    def test_user_registration(self):
        """Kullanıcı kayıt testi"""
        response = self.client.post(reverse('user_profile:register'), {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'complexpass123',
            'password2': 'complexpass123'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

    def test_user_logout(self):
        """Logout testi"""
        self.client.force_login(self.user)
        response = self.client.get(reverse('user_profile:logout'))
        self.assertEqual(response.status_code, 302)

class UserProfileViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_profile_view(self):
        """Profil görüntüleme testi"""
        response = self.client.get(reverse('user_profile:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile/profile.html')

    def test_profile_edit(self):
        """Profil düzenleme testi"""
        # Tüm zorunlu alanları dahil et
        response = self.client.post(reverse('user_profile:profile_edit'), {
            'username': 'updateduser',
            'email': 'updated@example.com',
            'pomodoro_duration': 25,  # EKLENDİ
            'daily_goal': 5           # EKLENDİ
        })
        
        # Hata ayıklama için response içeriğini yazdır
        if response.status_code != 302:
            print("Profile edit form errors:")
            if 'user_form' in response.context:
                print("User form errors:", response.context['user_form'].errors)
            if 'profile_form' in response.context:
                print("Profile form errors:", response.context['profile_form'].errors)
            # Response content'ini de yazdıralım
            print("Response content:", response.content.decode('utf-8')[:500])
        
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updateduser')

    def test_profile_view_page(self):
        """Profil görüntüleme sayfası testi"""
        response = self.client.get(reverse('user_profile:profile_view'))
        self.assertEqual(response.status_code, 200)

class BadgeSystemTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.badge_type = BadgeType.objects.create(
            name='Test Type',
            description='Test badge type'
        )
        self.badge = Badge.objects.create(
            name='Test Badge',
            badge_type=self.badge_type,
            description='Test badge description',
            criteria={'min_tasks': 5}
        )

    def test_badge_list_view(self):
        """Rozet listesi görüntüleme testi"""
        response = self.client.get(reverse('user_profile:badge_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile/badge_list.html')

    def test_badge_detail_view(self):
        """Rozet detay görüntüleme testi"""
        response = self.client.get(reverse('user_profile:badge_detail', args=[self.badge.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile/badge_detail.html')

    def test_force_badge_check(self):
        """Manuel rozet kontrolü testi - DEBUG"""
        # URL'i debug et
        url = reverse('user_profile:force_badge_check')
        print(f"Testing URL: {url}")
        
        response = self.client.get(url)
        print(f"Response status: {response.status_code}")
        
        # Eğer 404 ise, tüm URL pattern'larını listele
        if response.status_code == 404:
            from django.urls import get_resolver
            resolver = get_resolver()
            print("Available URL patterns:")
            for pattern in resolver.url_patterns:
                print(f" - {pattern}")
        
        self.assertEqual(response.status_code, 302)

class NotificationTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.notification = Notification.objects.create(
            user=self.user,
            message='Test notification',
            notification_type='info'
        )

    def test_notifications_view(self):
        """Bildirimler sayfası testi"""
        response = self.client.get(reverse('user_profile:notifications'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'user_profile/notifications.html')

    def test_clear_notifications(self):
        """Bildirim temizleme testi - DÜZELTİLDİ"""
        # AJAX header'ı ekle
        response = self.client.post(
            reverse('user_profile:clear_history_notifications'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        
    def test_mark_all_notifications_read(self):
        """Tüm bildirimleri okundu işaretleme testi - DÜZELTİLDİ"""
        # AJAX header'ı ekle  
        response = self.client.post(
            reverse('user_profile:mark_all_notifications_read'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

    def test_check_new_notifications(self):
        """Yeni bildirim kontrolü testi - DÜZELTİLDİ"""
        # AJAX header'ı ekle
        response = self.client.get(
            reverse('user_profile:check_new_notifications'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)

class PomodoroSettingsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.profile = self.user.profile  # BU SATIR EKLENDİ
        self.client.force_login(self.user)

    def test_update_pomodoro_duration(self):
        """Pomodoro süresi güncelleme testi"""
        response = self.client.post(
            reverse('user_profile:update_pomodoro'),
            data=json.dumps({'duration': 30}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.pomodoro_duration, 30)

class PasswordTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_password_change_view(self):
        """Şifre değiştirme sayfası testi"""
        response = self.client.get(reverse('user_profile:password_change'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_view(self):
        """Şifre sıfırlama sayfası testi"""
        response = self.client.get(reverse('user_profile:password_reset'))
        self.assertEqual(response.status_code, 200)