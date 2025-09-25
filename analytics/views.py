
from django.shortcuts import render
from analytics.utils import (
    generate_completion_chart, 
    generate_timeline_chart,
    generate_productivity_chart,
    task_completion_stats,
    calculate_productivity_score,
    generate_daily_heatmap,
    generate_weekly_trends,
)
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.cache import cache_page
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from .models import UserAnalytics
import logging




logger = logging.getLogger(__name__)


@login_required
def analytics_dashboard(request):
    try:
        context = {
            'completion_chart': generate_completion_chart(request.user),
            'timeline_chart': generate_timeline_chart(request.user),
            'heatmap_chart': generate_daily_heatmap(request.user),
            'productivity_score': calculate_productivity_score(request.user),
            'stats': task_completion_stats(request.user),
            'weekly_trends': generate_weekly_trends(request.user)
        }
    except Exception as e:
        logger.error(f"Analiz sayfası hatası: {str(e)}")
        context = {
            'error': "Analiz verileri yüklenirken bir hata oluştu",
            'stats': {
                'completed': 0,
                'pending': 0,
                'total': 0,
                'last_update': "Hata"
            }
        }
    
    return render(request, 'analytics/dashboard.html', context)