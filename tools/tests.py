from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from tools.models import StudyNote

User = get_user_model()

class ToolsViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_tools_home(self):
        """Araçlar ana sayfası testi"""
        response = self.client.get(reverse('tools:home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools/home.html')

    def test_calculator_view(self):
        """Hesap makinesi testi"""
        response = self.client.get(reverse('tools:calculator'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools/calculator.html')

    def test_stopwatch_view(self):
        """Kronometre testi"""
        response = self.client.get(reverse('tools:stopwatch'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools/stopwatch.html')

    def test_timer_view(self):
        """Zamanlayıcı testi"""
        response = self.client.get(reverse('tools:timer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools/timer.html')

class StudyNoteCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)
        
        self.note = StudyNote.objects.create(
            user=self.user,
            title='Test Study Note',
            content='Test content for study note'
        )

    def test_study_note_list(self):
        """Çalışma notları listesi testi"""
        response = self.client.get(reverse('tools:study_notes_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools/study_notes_list.html')

    def test_study_note_create(self):
        """Çalışma notu oluşturma testi"""
        response = self.client.post(reverse('tools:study_note_create'), {
            'title': 'New Study Note',
            'content': 'New study note content'
        })
        # Başarılı oluşturma 302 döndürmeli (redirect)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(StudyNote.objects.filter(title='New Study Note').exists())

    def test_study_note_update(self):
        """Çalışma notu güncelleme testi"""
        response = self.client.post(reverse('tools:study_note_update', args=[self.note.pk]), {
            'title': 'Updated Study Note',
            'content': 'Updated content'
        })
        # Başarılı güncelleme 302 döndürmeli (redirect)
        self.assertEqual(response.status_code, 302)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, 'Updated Study Note')

    def test_study_note_detail(self):
        """Çalışma notu detay testi"""
        response = self.client.get(reverse('tools:study_note_detail', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'tools/study_note_detail.html')

    def test_study_note_delete(self):
        """Çalışma notu silme testi"""
        response = self.client.post(reverse('tools:study_note_delete', args=[self.note.pk]))
        # Başarılı silme 302 döndürmeli (redirect)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(StudyNote.objects.filter(pk=self.note.pk).exists())