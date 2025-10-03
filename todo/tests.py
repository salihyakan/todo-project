import json
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from todo.models import Task, Category
from datetime import datetime, timedelta

User = get_user_model()

class TaskCRUDTests(TestCase):
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
            description='Test Description',
            category=self.category,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )

    def test_task_list_view(self):
        """Görev listesi görüntüleme testi"""
        response = self.client.get(reverse('todo:task_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_list.html')

def test_task_create(self):
    """Görev oluşturma testi"""
    # Timezone-aware datetime kullan
    due_date = timezone.now() + timedelta(days=2)
    response = self.client.post(reverse('todo:task_create'), {
        'title': 'New Task',
        'description': 'New Description',
        'category': self.category.id,
    })
    
    # Hata ayıklama için response içeriğini yazdır
    if response.status_code != 302:
        print("Task create form errors:")
        if 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        # Response content'ini de yazdıralım
        print("Response content:", response.content.decode('utf-8')[:500])
    
    self.assertEqual(response.status_code, 302)
    self.assertTrue(Task.objects.filter(title='New Task').exists())

def test_task_update(self):
    """Görev güncelleme testi"""
    response = self.client.post(reverse('todo:task_update', args=[self.task.pk]), {
        'title': 'Updated Task',
        'description': 'Updated Description',
        'category': self.category.id,
    })
    
    # Hata ayıklama için response içeriğini yazdır
    if response.status_code != 302:
        print("Task update form errors:")
        if 'form' in response.context:
            print("Form errors:", response.context['form'].errors)
        print("Response content:", response.content.decode('utf-8')[:500])
    
    self.assertEqual(response.status_code, 302)
    self.task.refresh_from_db()
    self.assertEqual(self.task.title, 'Updated Task')

    def test_task_detail(self):
        """Görev detay görüntüleme testi"""
        response = self.client.get(reverse('todo:task_detail', args=[self.task.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/task_detail.html')

    def test_task_delete(self):
        """Görev silme testi"""
        response = self.client.post(reverse('todo:task_delete', args=[self.task.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_task_status_update_ajax(self):
        """AJAX ile görev durumu güncelleme testi"""
        response = self.client.post(
            reverse('todo:update_task_status', args=[self.task.pk]),
            {'status': 'completed'},
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

    def test_complete_task(self):
        """Görev tamamlama testi"""
        response = self.client.post(reverse('todo:complete_task', args=[self.task.pk]))
        # AJAX olmayan istek 302 döndürmeli (redirect)
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')

class CategoryCRUDTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_login(self.user)

    def test_category_create(self):
        """Kategori oluşturma testi"""
        response = self.client.post(reverse('todo:category_create'), {
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
        response = self.client.get(reverse('todo:category_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Category')

    def test_category_update(self):
        """Kategori güncelleme testi"""
        category = Category.objects.create(
            user=self.user,
            name='Update Category',
            color='#0000FF'
        )
        response = self.client.post(reverse('todo:category_update', args=[category.slug]), {
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
        response = self.client.post(reverse('todo:category_delete', args=[category.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_category_detail(self):
        """Kategori detay testi"""
        category = Category.objects.create(
            user=self.user,
            name='Detail Category',
            color='#00FFFF'
        )
        response = self.client.get(reverse('todo:category_detail', args=[category.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'todo/category_detail.html')

class TaskFilterTests(TestCase):
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
        
        self.completed_task = Task.objects.create(
            user=self.user,
            title='Completed Task',
            status='completed',
            category=self.category,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )
        
        self.pending_task = Task.objects.create(
            user=self.user,
            title='Pending Task',
            status='todo',
            category=self.category,
            due_date=timezone.now() + timezone.timedelta(days=1)
        )

    def test_filter_completed_tasks(self):
        """Tamamlanan görevleri filtreleme testi"""
        response = self.client.get(reverse('todo:task_list') + '?status=completed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Task')

    def test_search_tasks(self):
        """Görev arama testi"""
        response = self.client.get(reverse('todo:task_list') + '?search=Completed')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Completed Task')