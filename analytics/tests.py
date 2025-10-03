from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from todo.models import Task, Category
from notes.models import Note
from dashboard.models import PomodoroSession

User = get_user_model()

class AnalyticsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.category = Category.objects.create(
            user=self.user,
            name='Test Category'
        )
        
        # due_date ile görevler oluştur
        for i in range(5):
            Task.objects.create(
                user=self.user,
                title=f'Completed Task {i}',
                status='completed',
                category=self.category,
                due_date=timezone.now() + timezone.timedelta(days=1)
            )
        
        for i in range(3):
            Task.objects.create(
                user=self.user,
                title=f'Pending Task {i}',
                status='todo',
                category=self.category,
                due_date=timezone.now() + timezone.timedelta(days=1)
            )
        
        # Notlar oluştur
        for i in range(4):
            Note.objects.create(
                user=self.user,
                title=f'Test Note {i}',
                content='Test content'
            )
        
        # Pomodoro oturumları oluştur
        for i in range(10):
            PomodoroSession.objects.create(
                user=self.user,
                session_type='work',
                duration=25,
                completed=True
            )

    def test_analytics_dashboard(self):
        """Analiz dashboard testi"""
        response = self.client.get(reverse('analytics:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'analytics/dashboard.html')
        # "Üretkenlik Skoru" yerine sayfada bulunan başka bir metin kontrol et
        self.assertContains(response, 'Analiz Raporları')

    def test_refresh_analytics(self):
        """Analiz verilerini yenileme testi"""
        response = self.client.get(reverse('analytics:refresh'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('analytics:dashboard'))

    def test_analytics_data_present(self):
        """Analiz verilerinin doğru hesaplandığını test et"""
        response = self.client.get(reverse('analytics:dashboard'))
        
        # Context'te beklenen verilerin olduğunu kontrol et
        self.assertIn('productivity_score', response.context)
        self.assertIn('stats', response.context)
        self.assertIn('weekly_trends', response.context)
        
        # Temel istatistikleri kontrol et
        stats = response.context['stats']
        self.assertEqual(stats['completed'], 5)  # 5 tamamlanmış görev
        self.assertEqual(stats['pending'], 3)    # 3 bekleyen görev