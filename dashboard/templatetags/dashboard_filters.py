# dashboard/templatetags/dashboard_filters.py
from django import template
from todo.models import Task 


register = template.Library()

@register.filter(name='completion_rate')
def completion_rate(user):
    # Kullanıcının tamamlama oranını hesaplayın
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status='completed').count()
    
    if total_tasks > 0:
        return int((completed_tasks / total_tasks) * 100)
    return 0

