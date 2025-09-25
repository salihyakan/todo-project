from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from todo.models import Task
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed todo data'

    def handle(self, *args, **kwargs):
        user = User.objects.get(username='admin')  # Test kullanıcısı
        
        # Örnek görevler oluştur
        tasks = [
            {'title': 'Proje planını tamamla', 'priority': 'H'},
            {'title': 'Toplantı notlarını hazırla', 'priority': 'M'},
            {'title': 'E-posta yanıtları', 'priority': 'L'},
        ]
        
        for i, task_data in enumerate(tasks):
            Task.objects.create(
                user=user,
                title=task_data['title'],
                description=f"{task_data['title']} açıklaması",
                due_date=timezone.now() + timedelta(days=i+1),
                priority=task_data['priority']
            )
        
        self.stdout.write(self.style.SUCCESS('Todo test verileri başarıyla oluşturuldu'))