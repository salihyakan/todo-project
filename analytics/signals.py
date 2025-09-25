from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from todo.models import Task
from notes.models import Note
from analytics.models import UserAnalytics
from analytics.utils import update_analytics_data

@receiver([post_save, post_delete], sender=Task)
def update_task_analytics(sender, instance, **kwargs):
    update_analytics_data(instance.user)

@receiver([post_save, post_delete], sender=Note)
def update_note_analytics(sender, instance, **kwargs):
    update_analytics_data(instance.user)