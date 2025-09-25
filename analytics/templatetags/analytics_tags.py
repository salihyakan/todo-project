from django import template
from analytics.utils import task_completion_stats
from todo.models import Task

register = template.Library()

@register.simple_tag
def completion_rate(user):
    total_tasks = Task.objects.filter(user=user).count()
    completed_tasks = Task.objects.filter(user=user, status='completed').count()
    
    if total_tasks > 0:
        return round((completed_tasks / total_tasks) * 100)
    return 0

@register.inclusion_tag('analytics/stats_badge.html')
def stats_badge(user):
    stats = task_completion_stats(user)
    return {'stats': stats}

@register.filter
def div(value, arg):
    """Bölme işlemi için özel filtre"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """Çarpma işlemi için özel filtre"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0