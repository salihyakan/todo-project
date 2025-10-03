from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from notes.models import Note, Category
from todo.models import Task

User = get_user_model()

class NoteCRUDTests(TestCase):
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
            name='Test Category',
            color='#FF0000'
        )
        
        self.task = Task.objects.create(
            user=self.user,
            title='Test Task',
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        
        self.note = Note.objects.create(
            user=self.user,
            title='Test Note',
            content='Test Content',
            category=self.category
        )

    def test_note_list_view(self):
        """Not listesi görüntüleme testi"""
        response = self.client.get(reverse('notes:note_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_list.html')

def test_note_create(self):
    """Not oluşturma testi"""
    response = self.client.post(reverse('notes:note_create'), {
        'title': 'New Note',
        'content': 'New Content',
    })
    
    # Hata ayıklama için response içeriğini yazdır
    if response.status_code != 302:
        print("Note create form errors:")
        if 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        # Response content'ini de yazdıralım
        print("Response content:", response.content.decode('utf-8')[:500])
    
    self.assertEqual(response.status_code, 302)
    self.assertTrue(Note.objects.filter(title='New Note').exists())

def test_note_create_for_task(self):
    """Görev için not oluşturma testi"""
    response = self.client.post(reverse('notes:note_create_for_task', args=[self.task.id]), {
        'title': 'Task Note',
        'content': 'Task related content',
    })
    
    # Hata ayıklama için response içeriğini yazdır
    if response.status_code != 302:
        print("Note create for task form errors:")
        if 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        print("Response content:", response.content.decode('utf-8')[:500])
    
    self.assertEqual(response.status_code, 302)
    self.assertTrue(Note.objects.filter(task=self.task).exists())

def test_note_update(self):
    """Not güncelleme testi"""
    response = self.client.post(reverse('notes:note_update', args=[self.note.pk]), {
        'title': 'Updated Note',
        'content': 'Updated Content',
    })
    
    # Hata ayıklama için response içeriğini yazdır
    if response.status_code != 302:
        print("Note update form errors:")
        if 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        print("Response content:", response.content.decode('utf-8')[:500])
    
    self.assertEqual(response.status_code, 302)
    self.note.refresh_from_db()
    self.assertEqual(self.note.title, 'Updated Note')

    def test_note_detail(self):
        """Not detay görüntüleme testi"""
        response = self.client.get(reverse('notes:note_detail', args=[self.note.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/note_detail.html')

    def test_note_delete(self):
        """Not silme testi"""
        response = self.client.post(reverse('notes:note_delete', args=[self.note.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Note.objects.filter(pk=self.note.pk).exists())

def test_note_pinning(self):
    """Not sabitleme testi"""
    response = self.client.post(reverse('notes:note_update', args=[self.note.pk]), {
        'title': self.note.title,
        'content': self.note.content,
        'is_pinned': True
    })
    
    # Hata ayıklama için response içeriğini yazdır
    if response.status_code != 302:
        print("Note pinning form errors:")
        if 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        print("Response content:", response.content.decode('utf-8')[:500])
    
    self.assertEqual(response.status_code, 302)
    self.note.refresh_from_db()
    self.assertTrue(self.note.is_pinned)

    def test_task_notes(self):
        """Görev notları testi"""
        response = self.client.get(reverse('notes:task_notes', args=[self.task.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'notes/task_notes.html')

class NoteFilterTests(TestCase):
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
        
        self.pinned_note = Note.objects.create(
            user=self.user,
            title='Pinned Note',
            content='Pinned Content',
            is_pinned=True,
            category=self.category
        )
        
        self.normal_note = Note.objects.create(
            user=self.user,
            title='Normal Note',
            content='Normal Content',
            is_pinned=False,
            category=self.category
        )

    def test_filter_pinned_notes(self):
        """Sabitlenmiş notları filtreleme testi"""
        response = self.client.get(reverse('notes:note_list') + '?pinned=true')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pinned Note')

    def test_search_notes(self):
        """Not arama testi"""
        response = self.client.get(reverse('notes:note_list') + '?q=Pinned')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pinned Note')

class CategoryTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_category_creation(self):
        """Kategori oluşturma testi"""
        response = self.client.post(reverse('notes:category_create'), {
            'name': 'New Category',
            'color': '#00FF00'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Category.objects.filter(name='New Category').exists())

    def test_category_list(self):
        """Kategori listesi testi"""
        category = Category.objects.create(
            user=self.user,
            name='Test Category',
            color='#FF0000'
        )
        response = self.client.get(reverse('notes:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')

    def test_category_update(self):
        """Kategori güncelleme testi"""
        category = Category.objects.create(
            user=self.user,
            name='Update Category',
            color='#0000FF'
        )
        response = self.client.post(reverse('notes:category_update', args=[category.slug]), {
            'name': 'Updated Category',
            'color': '#FF00FF'
        })
        self.assertEqual(response.status_code, 302)
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Category')

    def test_category_delete(self):
        """Kategori silme testi"""
        category = Category.objects.create(
            user=self.user,
            name='Delete Category',
            color='#0000FF'
        )
        response = self.client.post(reverse('notes:category_delete', args=[category.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())