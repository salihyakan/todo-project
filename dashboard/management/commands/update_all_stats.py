from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from dashboard.models import DashboardStats

User = get_user_model()

class Command(BaseCommand):
    help = 'Update dashboard stats for all users'

    def handle(self, *args, **options):
        users = User.objects.all()
        self.stdout.write(f"Updating stats for {users.count()} users...")
        
        for user in users:
            try:
                stats, created = DashboardStats.objects.get_or_create(user=user)
                stats.update_stats()
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created stats for {user.username}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated stats for {user.username}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error for {user.username}: {e}'))