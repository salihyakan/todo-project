from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from todo.models import Task
from user_profile.models import Profile
from .models import DashboardStats, CalendarEvent, PomodoroSession  # DÜZELTİLDİ: tools yerine dashboard
from datetime import timedelta
import json
import pytz
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from notes.models import Note
from datetime import datetime, date
from django.views.decorators.http import require_http_methods
from .forms import CalendarEventForm 
import random
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from dashboard.models import PomodoroSession  # DÜZELTME: tools yerine dashboard

# Motivasyon sözleri listesi (15 adet)
MOTIVATION_QUOTES = [
    "Bugün, dün için endişelendiğin şeylerin çoğunu geride bıraktığın gün olacak.",
    "Küçük adımlar, büyük yolculukların başlangıcıdır. Her gün bir adım at.",
    "Başarı, düşe kalka ilerlemektir. Önemli olan her seferinde ayağa kalkmaktır.",
    "En iyi zamanı beklersen, hiç başlayamazsın. Şimdi başla, elindeki zaman en iyi zamandır.",
    "Hayatını değiştirmek için iki günün aynı olmaması yeterlidir: Bugün ve yarın.",
    "Her şey seninle başlar. İnanç, kararlılık ve sabır ile her şeyi başarabilirsin.",
    "Hayat, cesur adımlar atanları sever. Korkularını yen, hedeflerine ulaş.",
    "Başarı, sabrın ve emeğin meyvesidir. Her gün biraz daha çalış, biraz daha sabret.",
    "Hayat, sana verilenlerle değil, senin yaptıklarınla güzelleşir.",
    "Her gün yeni bir başlangıçtır. Dünü unut, bugünü yaşa, yarını bekle.",
    "Başarı, her gün tekrarlanan küçük çabaların toplamıdır.",
    "Hayat, senin onu nasıl gördüğünle ilgili. Olumlu düşün, olumlu olsun.",
    "Her şey seninle başlar. İçindeki gücü keşfet ve harekete geç.",
    "Hayat, senin onu nasıl yaşadığınla ilgili. Anı yaşa, mutlu ol.",
    "Başarı, hedefe giden yolda her gün attığın küçük adımlardır."
]

# Başarı sözleri listesi (20 adet)
SUCCESS_QUOTES = [
    "Başarı, hazırlık ve fırsatın buluştuğu yerdir.",
    "Büyük başarılar, büyük riskler almayı gerektirir.",
    "Başarı, sevdiğin işi yapmak ve yaptığın işi sevmektir.",
    "Hayattaki en büyük zafer hiç düşmemekte değil, her düştüğünde ayağa kalkmakta yatar.",
    "Başarı, sıradan şeyleri sıradışı şekilde yapmaktır.",
    "Başarının sırrı, amacın ne olduğunu bilmektir.",
    "En iyi intikam, muazzam bir başarıdır.",
    "Başarı, coşkuyu kaybetmeden başarısızlıktan başarısızlığa koşmaktır.",
    "Başarılı insanlar, başarı için gereken bedeli ödemekten kaçınmazlar.",
    "Başarı, küçük hataların, büyük kararlılıkla düzeltilmesidir.",
    "Başarı, sahip olduğunuz yeteneklerle değil, onları nasıl kullandığınızla ilgilidir.",
    "Büyük başarılar, küçük başlangıçlarla gelir.",
    "Başarı, sabrın ve emeğin meyvesidir.",
    "Her başarılı insanın arkasında, onu destekleyen biri vardır.",
    "Başarı, korkularınızın üstesinden gelmekle başlar.",
    "Başarılı olmak istiyorsanız, başarısızlığı kabul etmeyi reddedin.",
    "Başarı, hedeflerinize ulaşmak için gösterdiğiniz çabanın ölçüsüdür.",
    "Her başarı hikayesi, bir kişinin kendine olan inancıyla başlar.",
    "Başarı, sadece para kazanmak değil, fark yaratmaktır.",
    "Gerçek başarı, hem kendiniz hem de başkaları için değer yaratmaktır."
]

class HelpView(TemplateView):
    template_name = 'dashboard/help.html'

class FAQView(TemplateView):
    template_name = 'dashboard/faq.html'

class SupportView(TemplateView):
    template_name = 'dashboard/support.html'

class GuideView(TemplateView):
    template_name = 'dashboard/guide.html'

class ContactView(TemplateView):
    template_name = 'dashboard/contact.html'

class PrivacyView(TemplateView):
    template_name = 'dashboard/privacy.html'

class TermsView(TemplateView):
    template_name = 'dashboard/terms.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        months_tr = {
            1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan',
            5: 'Mayıs', 6: 'Haziran', 7: 'Temmuz', 8: 'Ağustos',
            9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'
        }
        last_updated = f"{start_of_week.day} {months_tr[start_of_week.month]} {start_of_week.year}"
        context['last_updated'] = last_updated
        return context

class CookiesView(TemplateView):
    template_name = 'dashboard/cookies.html'

class LicenseView(TemplateView):
    template_name = 'dashboard/license.html'

def landing_page(request):
    """Giriş yapmamış kullanıcılar için landing page"""
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    return render(request, 'dashboard/landing_page.html')

def get_daily_motivation():
    """Her gün için sırayla bir motivasyon sözü döndürür"""
    today = date.today()
    day_of_year = today.timetuple().tm_yday
    quote_index = (day_of_year - 1) % len(MOTIVATION_QUOTES)
    return MOTIVATION_QUOTES[quote_index]

def get_random_success_quotes(count=3):
    """Rastgele seçilmiş başarı sözleri döndürür"""
    return random.sample(SUCCESS_QUOTES, min(count, len(SUCCESS_QUOTES)))

def get_pomodoro_stats(user_id):
    """Basit pomodoro istatistikleri - Optimize edilmiş"""
    try:
        # DÜZELTME: tools yerine dashboard - import kaldırıldı
        user_sessions = PomodoroSession.objects.filter(user_id=user_id, completed=True)
        
        total_sessions = user_sessions.count()
        
        # Aggregate kullanarak toplam süreleri hesapla
        from django.db.models import Sum
        focus_time = user_sessions.filter(session_type='work').aggregate(
            total=Sum('duration')
        )['total'] or 0
        
        break_time = user_sessions.filter(session_type='break').aggregate(
            total=Sum('duration')
        )['total'] or 0
        
        # Günlük ortalama (son 7 gün)
        week_ago = timezone.now() - timedelta(days=7)
        recent_count = user_sessions.filter(created_at__gte=week_ago).count()
        daily_average = recent_count / 7 if recent_count > 0 else 0
        
        return {
            'total_sessions': total_sessions,
            'total_focus_time': focus_time,
            'total_break_time': break_time,
            'daily_average': round(daily_average, 1)
        }
    except Exception as e:
        print(f"Pomodoro stats error: {e}")
        return {
            'total_sessions': 0,
            'total_focus_time': 0,
            'total_break_time': 0,
            'daily_average': 0
        }

def get_recent_sessions(user_id, limit=10):
    """Son pomodoro oturumları - Optimize edilmiş"""
    try:
        # DÜZELTME: tools yerine dashboard
        # Sadece gerekli alanları seçerek optimizasyon
        sessions = PomodoroSession.objects.filter(
            user_id=user_id, 
            completed=True
        ).only('session_type', 'duration', 'created_at').order_by('-created_at')[:limit]
        
        session_list = []
        for session in sessions:
            session_list.append({
                'type': session.session_type,
                'duration': session.duration,
                'created_at': session.created_at.strftime('%d.%m.%Y %H:%M')
            })
        
        return session_list
    except Exception as e:
        print(f"Recent sessions error: {e}")
        return []

def store_pomodoro_session(user_id, session_type, duration):
    """Pomodoro oturumunu veritabanına kaydet - Her çalışma oturumu için +1"""
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        user = User.objects.get(id=user_id)
        
        # Oturumu kaydet
        PomodoroSession.objects.create(
            user=user,
            session_type=session_type,
            duration=duration,
            completed=True
        )
        
        # Dashboard istatistiklerini güncelle
        stats, created = DashboardStats.objects.get_or_create(user=user)
        stats.update_stats()
        
        print(f"Pomodoro session saved: user={user.username}, type={session_type}, duration={duration}")
    except Exception as e:
        print(f"Error saving pomodoro session: {e}")

def get_event_color(event_type):
    """Etkinlik türüne göre renk döndürür"""
    colors = {
        'task': '#3788d8',
        'note': '#ffc107',
        'event': '#28a745',
        'reminder': '#dc3545'
    }
    return colors.get(event_type, '#6c757d')

@login_required
def home(request):
    try:
        # Dashboard istatistiklerini güncelle
        stats, created = DashboardStats.objects.select_related('user').get_or_create(user=request.user)
        stats.update_stats()
        stats.refresh_from_db()
        print(f"Home stats: tasks={stats.tasks_completed}, pomodoros={stats.pomodoros_completed}, streak={stats.current_streak}")
    except Exception as e:
        print(f"Dashboard stats error: {e}")
        stats = type('obj', (object,), {
            'tasks_completed': 0,
            'pomodoros_completed': 0,
            'notes_created': 0,
            'current_streak': 0
        })()

    # GERÇEK ZAMANLI VERİLERİ HESAPLA
    from todo.models import Task
    from notes.models import Note
    
    total_tasks = Task.objects.filter(user=request.user).count()
    completed_tasks = Task.objects.filter(user=request.user, status='completed').count()
    pending_tasks = total_tasks - completed_tasks
    
    today = timezone.now().date()
    overdue_tasks = Task.objects.filter(
        user=request.user, 
        due_date__lt=today,
        status__in=['todo', 'in_progress']
    ).count()

    real_notes_count = Note.objects.filter(user=request.user).count()
    
    completion_rate = 0
    if total_tasks > 0:
        completion_rate = int((completed_tasks / total_tasks) * 100)
    
    # Bugünün görevleri
    todays_tasks = Task.objects.filter(
        user=request.user,
        due_date__date=today,
        status__in=['todo', 'in_progress']
    ).select_related('category').order_by('priority', 'due_date')[:5]
    
    # Son notlar
    recent_notes = Note.objects.filter(user=request.user).select_related('category', 'task').order_by('-created_at')[:5]
    
    try:
        profile = Profile.objects.select_related('user').get(user=request.user)
    except Profile.DoesNotExist:
        profile = type('obj', (object,), {
            'daily_goal': 0,
            'pomodoro_duration': 25
        })()
    
    daily_motivation = get_daily_motivation()
    random_success_quotes = get_random_success_quotes(3)
    
    context = {
        'todays_tasks': todays_tasks,
        'recent_notes': recent_notes,
        'stats': stats,
        'pomodoro_duration': getattr(profile, 'pomodoro_duration', 25),
        'daily_goal': getattr(profile, 'daily_goal', 0),
        'completion_rate': completion_rate,
        'completed_tasks_count': completed_tasks,
        'pending_tasks_count': pending_tasks,
        'overdue_tasks_count': overdue_tasks,
        'real_notes_count': real_notes_count,
        'daily_motivation': daily_motivation,
        'random_success_quotes': random_success_quotes,
    }
    
    return render(request, 'dashboard/home.html', context)

@login_required
def pomodoro_view(request):
    try:
        # select_related ile optimizasyon
        profile = Profile.objects.select_related('user').get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    
    # Basit istatistikler - Optimize edilmiş
    stats = get_pomodoro_stats(request.user.id)
    
    # Son oturumlar - Optimize edilmiş
    history = get_recent_sessions(request.user.id, 10)

    return render(request, 'dashboard/pomodoro.html', {
        'pomodoro_duration': profile.pomodoro_duration,
        'redis_stats': stats,
        'redis_history': history
    })

@login_required
def calendar_view(request):
    form = CalendarEventForm()
    
    turkiye_tz = pytz.timezone('Europe/Istanbul')
    start_date = timezone.now() - timedelta(days=30)
    end_date = timezone.now() + timedelta(days=365)
    
    # select_related ile optimizasyon
    events = CalendarEvent.objects.filter(
        user=request.user,
        start_date__gte=start_date,
        start_date__lte=end_date
    ).select_related('related_note', 'related_task')
    
    events_data = []
    for event in events:
        start_date_tz = event.start_date.astimezone(turkiye_tz)
        end_date_tz = event.end_date.astimezone(turkiye_tz) if event.end_date else None
        
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': start_date_tz.isoformat(),
            'end': end_date_tz.isoformat() if end_date_tz else None,
            'color': event.color,
            'extendedProps': {
                'type': event.event_type,
                'description': event.description,
                'url': event.get_absolute_url()
            }
        })
    
    context = {
        'form': form,
        'events_json': json.dumps(events_data)
    }
    return render(request, 'dashboard/calendar.html', context)

@login_required
@require_http_methods(["POST"])
def create_calendar_event(request):
    try:
        data = json.loads(request.body)
        start_date_str = data.get('start_date')
        
        turkiye_tz = pytz.timezone('Europe/Istanbul')
        
        try:
            naive_datetime = datetime.strptime(start_date_str, "%Y-%m-%dT%H:%M")
            start_date = turkiye_tz.localize(naive_datetime)
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Tarih formatı hatası: {str(e)}"
            }, status=400)
        
        end_date = None
        end_date_str = data.get('end_date')
        if end_date_str:
            try:
                naive_end = datetime.strptime(end_date_str, "%Y-%m-%dT%H:%M")
                end_date = turkiye_tz.localize(naive_end)
            except:
                pass
        
        event = CalendarEvent.objects.create(
            user=request.user,
            title=data.get('title'),
            description=data.get('description', ''),
            start_date=start_date,
            end_date=end_date,
            event_type=data.get('event_type'),
            reminder=None
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Etkinlik başarıyla oluşturuldu! Başlangıç ve bitiş zamanlarında otomatik bildirim gönderilecek.",
            "event_id": event.id,
            "event_url": event.get_absolute_url(),
            "start_date_local": start_date.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": f"Bir hata oluştu: {str(e)}"
        }, status=400)

@login_required
@require_http_methods(["GET"])
def get_calendar_events(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    
    try:
        if start and end:
            start_date = datetime.fromisoformat(start.replace('Z', ''))
            end_date = datetime.fromisoformat(end.replace('Z', ''))
        else:
            start_date = timezone.now() - timedelta(days=30)
            end_date = timezone.now() + timedelta(days=365)
    except:
        start_date = timezone.now() - timedelta(days=30)
        end_date = timezone.now() + timedelta(days=365)

    # select_related ile optimizasyon
    events = CalendarEvent.objects.filter(
        user=request.user,
        start_date__gte=start_date,
        start_date__lte=end_date
    ).select_related('related_note', 'related_task')

    events_data = []
    for event in events:
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat() if event.end_date else None,
            'color': event.color,
            'allDay': event.is_all_day,
            'extendedProps': {
                'type': event.event_type,
                'description': event.description,
                'url': event.get_absolute_url()
            }
        })
    
    return JsonResponse(events_data, safe=False)

@login_required
def day_detail_view(request, year, month, day):
    try:
        # Gelen parametreleri integer'a çevir ve kontrol et
        year_int = int(year)
        month_int = int(month)
        day_int = int(day)
        
        # Ay değerini kontrol et (1-12 arası olmalı)
        if not (1 <= month_int <= 12):
            raise ValueError("Ay değeri 1-12 arasında olmalıdır")
        
        # Gün değerini kontrol et (1-31 arası olmalı)
        if not (1 <= day_int <= 31):
            raise ValueError("Gün değeri 1-31 arasında olmalıdır")
        
        # Tarihi oluştur
        date_obj = timezone.datetime(year=year_int, month=month_int, day=day_int).date()
        
    except (ValueError, TypeError) as e:
        # Hata durumunda 404 sayfası göster
        from django.http import Http404
        raise Http404(f"Geçersiz tarih parametreleri: {e}")
    
    # Tarih aralığını belirle (o günün başından sonuna kadar)
    start_datetime = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.min.time()))
    end_datetime = timezone.make_aware(timezone.datetime.combine(date_obj, timezone.datetime.max.time()))

    # Kullanıcının o güne ait etkinliklerini getir - select_related ile optimizasyon
    events = CalendarEvent.objects.filter(
        user=request.user,
        start_date__gte=start_datetime,
        start_date__lte=end_datetime
    ).select_related('related_note', 'related_task').order_by('start_date')

    context = {
        'date': date_obj,
        'events': events,
    }
    return render(request, 'dashboard/day_detail.html', context)

@login_required
def event_detail_view(request, event_id):
    # select_related ile optimizasyon
    event = get_object_or_404(
        CalendarEvent.objects.select_related('related_note', 'related_task'), 
        id=event_id, 
        user=request.user
    )
    return render(request, 'dashboard/event_detail.html', {'event': event})

@csrf_exempt
@login_required
def save_pomodoro_session(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            store_pomodoro_session(
                request.user.id,
                data['type'],
                data['duration']
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            print(f"Error saving pomodoro session: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def event_detail_json(request, event_id):
    # select_related ile optimizasyon
    event = get_object_or_404(
        CalendarEvent.objects.select_related('related_note', 'related_task'), 
        id=event_id, 
        user=request.user
    )
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