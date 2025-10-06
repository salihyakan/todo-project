from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import List, ListItem
from .forms import ListForm, ListItemForm

User = get_user_model()

class ListModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.list = List.objects.create(
            user=self.user,
            title='Test Liste',
            description='Test açıklama',
            list_type='shopping',
            color='#FFD700'
        )

    def test_list_creation(self):
        self.assertEqual(self.list.title, 'Test Liste')
        self.assertEqual(self.list.user, self.user)
        self.assertEqual(self.list.list_type, 'shopping')
        self.assertTrue(isinstance(self.list, List))

    def test_list_str_representation(self):
        self.assertEqual(str(self.list), 'Test Liste - testuser')

    def test_list_progress_calculation(self):
        # Boş liste için ilerleme
        self.assertEqual(self.list.progress_percentage(), 0)
        
        # Tamamlanmamış öğe ekle
        ListItem.objects.create(
            list=self.list,
            content='Test madde',
            completed=False
        )
        self.assertEqual(self.list.progress_percentage(), 0)
        
        # Tamamlanmış öğe ekle
        ListItem.objects.create(
            list=self.list,
            content='Tamamlanmış madde',
            completed=True
        )
        self.assertEqual(self.list.progress_percentage(), 50)

class ListItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.list = List.objects.create(
            user=self.user,
            title='Test Liste'
        )
        self.item = ListItem.objects.create(
            list=self.list,
            content='Test madde',
            priority='high'
        )

    def test_item_creation(self):
        self.assertEqual(self.item.content, 'Test madde')
        self.assertEqual(self.item.priority, 'high')
        self.assertFalse(self.item.completed)

    def test_item_str_representation(self):
        self.assertEqual(str(self.item), '○ Test madde')
        self.item.completed = True
        self.item.save()
        self.assertEqual(str(self.item), '✓ Test madde')

class ListViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.list = List.objects.create(
            user=self.user,
            title='Test Liste'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_list_list_view(self):
        response = self.client.get(reverse('lists:list_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list_list.html')
        self.assertContains(response, 'Test Liste')

    def test_list_detail_view(self):
        response = self.client.get(reverse('lists:list_detail', args=[self.list.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lists/list_detail.html')
        self.assertContains(response, self.list.title)

    def test_list_create_view(self):
        response = self.client.post(reverse('lists:list_create'), {
            'title': 'Yeni Liste',
            'list_type': 'todo',
            'color': '#FFD700'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(List.objects.filter(title='Yeni Liste').exists())

    def test_list_update_view(self):
        response = self.client.post(reverse('lists:list_edit', args=[self.list.id]), {
            'title': 'Güncellenmiş Liste',
            'list_type': 'shopping',
            'color': '#FFA500'
        })
        self.assertEqual(response.status_code, 302)
        self.list.refresh_from_db()
        self.assertEqual(self.list.title, 'Güncellenmiş Liste')

    def test_list_delete_view(self):
        response = self.client.post(reverse('lists:list_delete', args=[self.list.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(List.objects.filter(id=self.list.id).exists())

class ListFormsTest(TestCase):
    def test_list_form_valid(self):
        form = ListForm(data={
            'title': 'Test Liste',
            'list_type': 'todo',
            'color': '#FFD700'
        })
        self.assertTrue(form.is_valid())

    def test_list_form_invalid(self):
        form = ListForm(data={'title': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_list_item_form_valid(self):
        form = ListItemForm(data={
            'content': 'Test madde',
            'priority': 'medium'
        })
        self.assertTrue(form.is_valid())

    def test_list_item_form_invalid(self):
        form = ListItemForm(data={'content': ''})
        self.assertFalse(form.is_valid())
        self.assertIn('content', form.errors)