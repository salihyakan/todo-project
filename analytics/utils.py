import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.db.models import Count, Case, When, IntegerField, F, Sum, Avg, Q
from todo.models import Task
from notes.models import Note
from dashboard.models import DashboardStats
from django.db.models.functions import TruncDate, ExtractWeekDay, TruncDay
import numpy as np
from datetime import datetime, timedelta
from .models import UserAnalytics
from django.utils import timezone


def task_completion_stats(user):
    """Daha detaylı istatistik hesaplama"""
    try:
        completed = Task.objects.filter(user=user, status='completed').count() or 0
        pending = Task.objects.filter(user=user).exclude(status='completed').count() or 0
        total = completed + pending
        
        # Öncelik dağılımı
        high_priority = Task.objects.filter(user=user, priority='H').count()
        medium_priority = Task.objects.filter(user=user, priority='M').count()
        low_priority = Task.objects.filter(user=user, priority='L').count()
        
        # Not sayısı
        notes_count = Note.objects.filter(user=user).count()
        
        # Pomodoro sayısı
        try:
            pomodoros_count = DashboardStats.objects.get(user=user).pomodoros_completed
        except DashboardStats.DoesNotExist:
            pomodoros_count = 0
        
        # Ortalama tamamlama süresi (basit hesaplama)
        avg_completion_time = 2.3  # Bu gerçek veriyle değiştirilebilir
        
        categories = Task.objects.filter(user=user).values(
            'category__name', 
            'category__color'
        ).annotate(
            total=Count('id'),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField()))
        )
        
        # Kategorisiz görevler
        uncategorized = {
            'category__name': "Kategorisiz",
            'category__color': "#6c757d",
            'total': Task.objects.filter(user=user, category__isnull=True).count() or 0,
            'completed': Task.objects.filter(user=user, category__isnull=True, status='completed').count() or 0
        }
        
        result = list(categories)
        if uncategorized['total'] > 0:
            result.append(uncategorized)
            
        return {
            'completed': completed,
            'pending': pending,
            'total': total,
            'categories': result,
            'tasks': {
                'H': high_priority,
                'M': medium_priority,
                'L': low_priority
            },
            'notes_count': notes_count,
            'pomodoros_count': pomodoros_count,
            'avg_completion_time': avg_completion_time,
            'last_update': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
    except Exception as e:
        print(f"Analiz hatası: {str(e)}")
        return {
            'completed': 0,
            'pending': 0,
            'total': 0,
            'categories': [],
            'tasks': {'H': 0, 'M': 0, 'L': 0},
            'notes_count': 0,
            'pomodoros_count': 0,
            'avg_completion_time': 0,
            'last_update': "Hata"
        }

def calculate_productivity_score(user):
    """Kullanıcı verimlilik skorunu hesaplar"""
    completed_tasks = Task.objects.filter(user=user, status='completed').count()
    total_tasks = Task.objects.filter(user=user).count()
    notes_count = Note.objects.filter(user=user).count()
    
    if total_tasks == 0:
        return 0
    
    task_ratio = completed_tasks / total_tasks
    productivity = (task_ratio * 70) + (notes_count * 0.3)  # Ağırlıklı formül
    
    return min(100, round(productivity, 1))

def generate_plot_image(plt):
    """Matplotlib grafiklerini base64 formatında döndürür"""
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    plt.clf()  # Aktif figürü temizle
    plt.close()  # Figürü kapat
    return base64.b64encode(image_png).decode('utf-8')
    
def generate_completion_chart(user):
    """Daha küçük ve optimize edilmiş pie chart"""
    stats = task_completion_stats(user)
    labels = ['Tamamlandı', 'Beklemede']
    sizes = [stats['completed'], stats['pending']]
    
    if sum(sizes) == 0:
        sizes = [1, 0]
        labels = ['Veri Yok', '']
    
    plt.figure(figsize=(3, 3))  # Daha küçük boyut - 3x3 inç
    colors = ['#1cc88a', '#f6c23e']
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors,
            startangle=90, textprops={'fontsize': 8})  # Yazı boyutunu küçült
    plt.title('Görev Durumu', fontsize=10, fontweight='bold')  # Başlık boyutunu küçült
    plt.tight_layout()
    
    return generate_plot_image(plt)

def generate_timeline_chart(user):
    """Optimize edilmiş timeline chart"""
    plt.figure(figsize=(6, 2.5))  # Daha küçük boyut - 6x2.5 inç
    
    # Örnek veri - gerçek uygulamada veritabanından çekilecek
    dates = ['01/10', '05/10', '10/10', '15/10', '20/10', '25/10', '30/10']
    completed_tasks = [3, 5, 2, 8, 6, 4, 7]
    
    plt.plot(dates, completed_tasks, marker='o', linewidth=1.5, color='#36b9cc', markersize=4)
    plt.fill_between(dates, completed_tasks, alpha=0.3, color='#36b9cc')
    plt.title('Günlük Tamamlanan Görevler', fontsize=10, fontweight='bold')
    plt.xticks(rotation=45, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return generate_plot_image(plt)

def generate_productivity_chart(user):
    """Verimlilik grafiği oluştur"""
    plt.figure(figsize=(6, 2.5))  # Küçük boyut
    
    # Örnek veri
    dates = ['Hafta1', 'Hafta2', 'Hafta3', 'Hafta4']
    productivity_scores = [65, 70, 80, 75]
    
    plt.plot(dates, productivity_scores, marker='s', linewidth=1.5, color='#4e73df', markersize=4)
    plt.fill_between(dates, productivity_scores, alpha=0.3, color='#4e73df')
    plt.title('Haftalık Verimlilik Eğrisi', fontsize=10, fontweight='bold')
    plt.xlabel('Haftalar', fontsize=8)
    plt.ylabel('Verimlilik', fontsize=8)
    plt.xticks(fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    return generate_plot_image(plt)

def update_analytics_data(user):
    """Tüm analiz verilerini günceller"""
    stats = task_completion_stats(user)
    productivity = calculate_productivity_score(user)
    weekly = generate_weekly_trends(user)
    
    analytics, _ = UserAnalytics.objects.get_or_create(user=user)
    analytics.task_stats = stats
    analytics.productivity_score = productivity
    analytics.weekly_trends = weekly
    analytics.save()

def task_completion_stats(user):
    """Daha güvenli istatistik hesaplama"""
    try:
        completed = Task.objects.filter(user=user, status='completed').count() or 0
        pending = Task.objects.filter(user=user).exclude(status='completed').count() or 0
        
        categories = Task.objects.filter(user=user).values(
            'category__name', 
            'category__color'
        ).annotate(
            total=Count('id'),
            completed=Count(Case(When(status='completed', then=1), output_field=IntegerField()))
        )
        
        # Kategorisiz görevler
        uncategorized = {
            'category__name': "Kategorisiz",
            'category__color': "#6c757d",
            'total': Task.objects.filter(user=user, category__isnull=True).count() or 0,
            'completed': Task.objects.filter(user=user, category__isnull=True, status='completed').count() or 0
        }
        
        result = list(categories)
        if uncategorized['total'] > 0:
            result.append(uncategorized)
            
        return {
            'completed': completed,
            'pending': pending,
            'total': completed + pending,
            'categories': result,
            'last_update': datetime.now().strftime('%d.%m.%Y %H:%M')
        }
    except Exception as e:
        print(f"Analiz hatası: {str(e)}")
        return {
            'completed': 0,
            'pending': 0,
            'total': 0,
            'categories': [],
            'last_update': "Hata"
        }

def generate_weekly_trends(user):
    """7 günlük veri trendleri - Türkçe ve doğru verilerle"""
    # Türkçe gün isimleri
    turkish_days = {
        0: 'Pazartesi',
        1: 'Salı',
        2: 'Çarşamba',
        3: 'Perşembe',
        4: 'Cuma',
        5: 'Cumartesi',
        6: 'Pazar'
    }
    
    # Son 7 günü al
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=6)
    
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        # Tamamlanan görevler
        completed = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date=current_date
        ).count()
        
        # Oluşturulan görevler
        created = Task.objects.filter(
            user=user,
            created_at__date=current_date
        ).count()
        
        # Not sayısı
        notes_count = Note.objects.filter(
            user=user,
            created_at__date=current_date
        ).count()
        
        # Pomodoro sayısı (dashboard stats'ten al)
        try:
            pomodoro_count = DashboardStats.objects.get(user=user).pomodoros_completed
        except DashboardStats.DoesNotExist:
            pomodoro_count = 0
        
        # Verimlilik hesapla
        efficiency = (completed / created * 100) if created > 0 else 0
        
        daily_data.append({
            'date': current_date.strftime('%Y-%m-%d'),
            'day_name': turkish_days[current_date.weekday()],
            'completed': completed,
            'created': created,
            'notes_count': notes_count,
            'pomodoro_count': pomodoro_count // 7,  # Haftalık ortalama
            'efficiency': efficiency
        })
        
        current_date += timedelta(days=1)
    
    return daily_data


def generate_daily_heatmap(user):
    """Geliştirilmiş heatmap grafiği"""
    plt.figure(figsize=(3, 2))  # Çok küçük boyut
    
    # Örnek heatmap verisi
    days = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz']
    weeks = ['H1', 'H2', 'H3', 'H4']
    
    # Örnek aktivite verisi
    data = np.random.randint(0, 10, size=(4, 7))
    
    sns.heatmap(data, annot=True, fmt='d', cmap='YlOrRd', 
                xticklabels=days, yticklabels=weeks,
                cbar_kws={'label': 'Aktivite'}, annot_kws={'size': 6})
    plt.title('4 Haftalık Aktivite', fontsize=9, fontweight='bold')
    plt.tight_layout()
    
    return generate_plot_image(plt)

def calculate_real_work_time(user):
    """Gerçek çalışma süresini hesapla (pomodoro bazlı)"""
    try:
        stats = DashboardStats.objects.get(user=user)
        # Her pomodoro 25 dakika kabul edelim
        total_minutes = stats.pomodoros_completed * 25
        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours} saat {minutes} dakika"
    except DashboardStats.DoesNotExist:
        return "0 saat 0 dakika"

def calculate_daily_work_average(user):
    """Günlük ortalama çalışma süresi"""
    try:
        stats = DashboardStats.objects.get(user=user)
        # Kullanıcının kayıtlı olduğu gün sayısı
        days_since_joined = (timezone.now() - user.date_joined).days
        if days_since_joined == 0:
            days_since_joined = 1
        
        daily_pomodoros = stats.pomodoros_completed / days_since_joined
        daily_minutes = daily_pomodoros * 25
        hours = int(daily_minutes // 60)
        minutes = int(daily_minutes % 60)
        return f"{hours} saat {minutes} dakika"
    except DashboardStats.DoesNotExist:
        return "0 saat 0 dakika"

def calculate_avg_completion_time(user):
    """Ortalama görev tamamlama süresi (gün cinsinden)"""
    completed_tasks = Task.objects.filter(
        user=user, 
        status='completed', 
        completed_at__isnull=False,
        created_at__isnull=False
    )
    
    if not completed_tasks.exists():
        return 0
    
    total_seconds = 0
    for task in completed_tasks:
        if task.completed_at and task.created_at:
            duration = task.completed_at - task.created_at
            total_seconds += duration.total_seconds()
    
    avg_seconds = total_seconds / completed_tasks.count()
    avg_days = avg_seconds / (24 * 3600)  # Saniyeden güne çevir
    return round(avg_days, 1)

def calculate_on_time_completion_rate(user):
    """Zamanında tamamlama oranı"""
    completed_tasks = Task.objects.filter(user=user, status='completed')
    if not completed_tasks.exists():
        return 0
    
    on_time_count = 0
    for task in completed_tasks:
        if task.completed_at and task.completed_at <= task.due_date:
            on_time_count += 1
    
    return round((on_time_count / completed_tasks.count()) * 100)

def get_most_used_category(user):
    """En sık kullanılan kategori"""
    from todo.models import Category
    # En çok göreve sahip kategori
    category_stats = Category.objects.filter(user=user).annotate(
        task_count=Count('tasks')
    ).order_by('-task_count').first()
    
    return category_stats.name if category_stats else "Kategori yok"

def get_notes_statistics(user):
    """Not istatistikleri"""
    total_notes = Note.objects.filter(user=user).count()
    
    # Bu ay eklenen notlar
    current_month = timezone.now().month
    current_year = timezone.now().year
    monthly_notes = Note.objects.filter(
        user=user,
        created_at__month=current_month,
        created_at__year=current_year
    ).count()
    
    # Ortalama not uzunluğu
    notes = Note.objects.filter(user=user)
    if notes.exists():
        avg_length = sum(len(note.content) for note in notes) / notes.count()
    else:
        avg_length = 0
    
    return {
        'total': total_notes,
        'monthly': monthly_notes,
        'avg_length': round(avg_length)
    }

def get_pomodoro_statistics(user):
    """Pomodoro istatistikleri"""
    try:
        stats = DashboardStats.objects.get(user=user)
        total_pomodoros = stats.pomodoros_completed
        
        # Günlük ortalama
        days_since_joined = (timezone.now() - user.date_joined).days
        if days_since_joined == 0:
            days_since_joined = 1
        daily_avg = total_pomodoros / days_since_joined
        
        # Başarı oranı (basit bir hesaplama)
        completed_tasks = Task.objects.filter(user=user, status='completed').count()
        success_rate = min(100, (completed_tasks / total_pomodoros * 100)) if total_pomodoros > 0 else 0
        
        return {
            'total': total_pomodoros,
            'daily_avg': round(daily_avg, 1),
            'success_rate': round(success_rate)
        }
    except DashboardStats.DoesNotExist:
        return {'total': 0, 'daily_avg': 0, 'success_rate': 0}

def get_productivity_peak_hours(user):
    """En verimli çalışma saatleri"""
    # Basit bir analiz - gerçek uygulamada daha detaylı olabilir
    return "09:00 - 12:00"