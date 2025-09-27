from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from todo.models import Task
from user_profile.models import Profile
from .models import DashboardStats, CalendarEvent
from datetime import timedelta
import json
import pytz
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notes.models import Note
from datetime import datetime
from django.views.decorators.http import require_http_methods

# Redis utils kaldırıldı - basit alternatifler eklendi
def get_pomodoro_stats(user_id):
    """Basit pomodoro istatistikleri (Redis olmadan)"""
    return {
        'total_sessions': 0,
        'total_focus_time': 0,
        'daily_average': 0
    }

def get_recent_sessions(user_id, limit=10):
    """Son pomodoro oturumları (Redis olmadan)"""
    return []

def store_pomodoro_session(user_id, session_type, duration):
    """Pomodoro oturumunu kaydet (Redis olmadan)"""
    # Basitçe database'e kaydedebilirsiniz veya geçici olarak boş bırakın
    print(f"Pomodoro session: user={user_id}, type={session_type}, duration={duration}")
    # İsterseniz burada basit bir database modeli kullanabilirsiniz

# Etkinlik türüne göre renk döndürür
def get_event_color(event_type):
    colors = {
        'task': '#3788d8',     # Mavi
        'note': '#ffc107',     # Sarı
        'event': '#28a745',    # Yeşil
        'reminder': '#dc3545'  # Kırmızı
    }
    return colors.get(event_type, '#6c757d')  # Gri

@login_required
def home(request):
    stats, created = DashboardStats.objects.get_or_create(user=request.user)
    stats.update_stats()
    
    # Tamamlama oranını hesapla
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = int((completed_tasks / total_tasks) * 100)

    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    
    todays_tasks = Task.objects.filter(
        user=request.user,
        due_date__date__range=[today, tomorrow],
        status__in=['todo', 'in_progress']
    ).order_by('priority', 'due_date')[:5]
    
    recent_tasks = Task.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    recent_notes = Note.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    profile = Profile.objects.get(user=request.user)
    
    goal_progress = min(stats.tasks_completed, profile.daily_goal)
    
    if profile.daily_goal > 0:
        goal_percentage = min(100, int((stats.tasks_completed / profile.daily_goal) * 100))
    else:
        goal_percentage = 0
    
    context = {
        'todays_tasks': todays_tasks,
        'recent_tasks': recent_tasks,
        'recent_notes': recent_notes,
        'stats': stats,
        'pomodoro_duration': profile.pomodoro_duration,
        'daily_goal': profile.daily_goal,
        'goal_progress': goal_progress,
        'goal_percentage': goal_percentage,
        'completion_rate': completion_rate,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def pomodoro_view(request):
    profile = Profile.objects.get(user=request.user)
    stats = get_pomodoro_stats(request.user.id)
    history = get_recent_sessions(request.user.id, 10)
    
    return render(request, 'dashboard/pomodoro.html', {
        'pomodoro_duration': profile.pomodoro_duration,
        'redis_stats': stats,
        'redis_history': history
    })

@login_required
def calendar_view(request):
    return render(request, 'dashboard/calendar.html')

@login_required
@require_http_methods(["POST"])
def create_calendar_event(request):
    data = json.loads(request.body)
    start_date_str = data.get('start_date')
    
    # Saat dilimi düzeltmesi: Gelen tarihi Türkiye saat dilimine göre işle
    try:
        naive_datetime = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
        turkiye_tz = pytz.timezone('Europe/Istanbul')
        start_date = turkiye_tz.localize(datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M"))
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Tarih formatı hatası: {str(e)}"
        }, status=400)
    
    # Hatırlatıcı bilgisini al
    reminder = data.get('reminder')
    if reminder:
        reminder = int(reminder)
    
    event = CalendarEvent.objects.create(
        user=request.user,
        title=data.get('title'),
        description=data.get('description', ''),
        start_date=start_date,
        event_type=data.get('event_type'),
        reminder=reminder
    )
    
    return JsonResponse({
        "status": "success",
        "message": "Etkinlik başarıyla oluşturuldu!",
        "event_id": event.id,
        "event_url": event.get_absolute_url(),
        "start_date_utc": start_date.astimezone(pytz.utc).isoformat(),
        "start_date_local": start_date.isoformat()
    })

@login_required
@require_http_methods(["GET"])
def get_calendar_events(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    turkiye_tz = pytz.timezone('Europe/Istanbul')
    
    try:
        # Tarihleri zaman dilimiyle birlikte işle
        start_date = turkiye_tz.localize(datetime.strptime(start, "%Y-%m-%dT%H:%M:%S"))
        end_date = turkiye_tz.localize(datetime.strptime(end, "%Y-%m-%dT%H:%M:%S"))
    except:
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now() + timedelta(days=30)

    events = CalendarEvent.objects.filter(
        user=request.user,
        start_date__gte=start_date,
        start_date__lte=end_date
    )

    events_data = []
    for event in events:
        # Etkinlik zamanını Türkiye saat dilimine dönüştür
        start_date_tz = event.start_date.astimezone(turkiye_tz)
        end_date_tz = event.end_date.astimezone(turkiye_tz) if event.end_date else None
        
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': start_date_tz.isoformat(),
            'end': end_date_tz.isoformat() if end_date_tz else None,
            'color': event.color,
            'allDay': event.is_all_day,
            'extendedProps': {
                'type': event.event_type,
                'description': event.description,
                'reminder': event.reminder,
                'reminder_time': event.reminder_time.astimezone(turkiye_tz).isoformat() if event.reminder_time else None,
                'url': event.get_absolute_url()
            }
        })
    return JsonResponse(events_data, safe=False)

@login_required
def day_detail_view(request, year, month, day):
    date = timezone.datetime(year=year, month=month, day=day).date()
    start_datetime = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.min.time()))
    end_datetime = timezone.make_aware(timezone.datetime.combine(date, timezone.datetime.max.time()))

    events = CalendarEvent.objects.filter(
        user=request.user,
        start_date__gte=start_datetime,
        start_date__lte=end_datetime
    ).order_by('start_date')

    context = {
        'date': date,
        'events': events,
    }
    return render(request, 'dashboard/day_detail.html', context)

@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id, user=request.user)
    return render(request, 'dashboard/event_detail.html', {'event': event})

@csrf_exempt
@login_required
def save_pomodoro_session(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        store_pomodoro_session(
            request.user.id,
            data['type'],
            data['duration']
        )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def event_detail_json(request, event_id):
    event = get_object_or_404(CalendarEvent, id=event_id, user=request.user)
    return JsonResponse({
        'id': event.id,
        'title': event.title,
        'start_date': event.start_date.isoformat(),
        'end_date': event.end_date.isoformat() if event.end_date else None,
        'event_type': event.event_type,
        'description': event.description,
        'color': event.color,
        'url': event.get_absolute_url()
    })