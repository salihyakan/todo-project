from django.shortcuts import render, redirect
from analytics.utils import (
    generate_completion_chart, 
    task_completion_stats,
    calculate_productivity_score,
    generate_weekly_trends,
    update_analytics_data,
    # Yeni fonksiyonları import edelim
    calculate_real_work_time,
    calculate_daily_work_average,
    calculate_avg_completion_time,
    calculate_on_time_completion_rate,
    get_most_used_category,
    get_notes_statistics,
    get_pomodoro_statistics,
    get_productivity_peak_hours
)
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def analytics_dashboard(request):
    try:
        # Verileri güncelle
        update_analytics_data(request.user)
        
        # Gerçek verileri hesapla
        work_time = calculate_real_work_time(request.user)
        daily_work_time = calculate_daily_work_average(request.user)
        avg_completion_time = calculate_avg_completion_time(request.user)
        on_time_rate = calculate_on_time_completion_rate(request.user)
        most_used_category = get_most_used_category(request.user)
        notes_stats = get_notes_statistics(request.user)
        pomodoro_stats = get_pomodoro_statistics(request.user)
        peak_hours = get_productivity_peak_hours(request.user)
        
        context = {
            'completion_chart': generate_completion_chart(request.user),
            'productivity_score': calculate_productivity_score(request.user),
            'stats': task_completion_stats(request.user),
            'weekly_trends': generate_weekly_trends(request.user),
            # Gerçek veriler
            'work_time': work_time,
            'daily_work_time': daily_work_time,
            'avg_completion_time': avg_completion_time,
            'on_time_rate': on_time_rate,
            'most_used_category': most_used_category,
            'notes_stats': notes_stats,
            'pomodoro_stats': pomodoro_stats,
            'peak_hours': peak_hours,
        }
    except Exception as e:
        logger.error(f"Analiz sayfası hatası: {str(e)}")
        context = {
            'error': "Analiz verileri yüklenirken bir hata oluştu",
            'stats': {
                'completed': 0,
                'pending': 0,
                'total': 0,
                'categories': [],
                'last_update': "Hata"
            },
            'weekly_trends': [],
            'productivity_score': 0,
            'work_time': "0 saat 0 dakika",
            'daily_work_time': "0 saat 0 dakika",
            'avg_completion_time': 0,
            'on_time_rate': 0,
            'most_used_category': "Veri yok",
            'notes_stats': {'total': 0, 'monthly': 0, 'avg_length': 0},
            'pomodoro_stats': {'total': 0, 'daily_avg': 0, 'success_rate': 0},
            'peak_hours': "Veri yok",
        }
    
    return render(request, 'analytics/dashboard.html', context)

@login_required
def refresh_analytics(request):
    """Manuel olarak verileri güncelle"""
    try:
        update_analytics_data(request.user)
        messages.success(request, "Analiz verileri başarıyla güncellendi!")
    except Exception as e:
        logger.error(f"Veri güncelleme hatası: {str(e)}")
        messages.error(request, "Veri güncelleme sırasında bir hata oluştu!")
    
    return redirect('analytics:dashboard')