from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class UserAnalytics(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='analytics')
    last_updated = models.DateTimeField(auto_now=True)
    task_stats = models.JSONField(default=dict)
    productivity_score = models.FloatField(default=0)
    weekly_trends = models.JSONField(default=list)
    
    class Meta:
        verbose_name_plural = "User Analytics"
        indexes = [
            models.Index(fields=['user', 'last_updated']),
        ]
    
    def __str__(self):
        return f"{self.user.username} Analytics"

@receiver(post_save, sender=User)
def create_user_analytics(sender, instance, created, **kwargs):
    if created:
        UserAnalytics.objects.create(user=instance)