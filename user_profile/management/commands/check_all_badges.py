from django.core.management.base import BaseCommand
from user_profile.models import Profile
from user_profile.utils import check_user_badges

class Command(BaseCommand):
    help = 'Tüm kullanıcılar için rozet kontrollerini çalıştırır'
    
    def handle(self, *args, **options):
        profiles = Profile.objects.all()
        for profile in profiles:
            check_user_badges(profile)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'{profiles.count()} kullanıcı için rozet kontrolleri tamamlandı.'
            )
        )