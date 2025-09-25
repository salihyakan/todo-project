import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from django.db.models import Count, Case, When, IntegerField, F
from todo.models import Task
from django.db.models.functions import TruncDate, ExtractWeekDay
import numpy as np
from notes.models import Note
from datetime import datetime, timedelta
from .models import UserAnalytics



def task_completion_stats(user):
    completed = Task.objects.filter(user=user, status='completed').count()
    pending = Task.objects.filter(user=user).exclude(status='completed').count()
    
    # Kategori kontrolünü düzeltiyoruz
    categories = Task.objects.filter(user=user).values(
        'category__name', 
        'category__color'
    ).annotate(
        total=Count('id'),
        completed=Count(Case(When(status='completed', then=1), output_field=IntegerField())
    ))
    
    # Null kategorileri işle
    uncategorized = {
        'category__name': "Kategorisiz",
        'category__color': "#6c757d",
        'total': Task.objects.filter(user=user, category__isnull=True).count(),
        'completed': Task.objects.filter(user=user, category__isnull=True, status='completed').count()
    }
    
    # Kategorisizleri listeye ekle
    result = list(categories)
    if uncategorized['total'] > 0:
        result.append(uncategorized)
    
    return {
        'completed': completed,
        'pending': pending,
        'categories': result
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
    """Daha güvenli pie chart oluşturma"""
    stats = task_completion_stats(user)
    labels = ['Tamamlandı', 'Beklemede']
    sizes = [stats['completed'], stats['pending']]
    
    # NaN ve sıfır değer kontrolü
    if sum(sizes) == 0:
        sizes = [1, 1]  # Minimum değerler
        labels = ['Veri Yok', '']
    
    plt.figure(figsize=(6, 6))
    plt.pie(
        sizes, 
        labels=labels, 
        autopct=lambda p: f'{p:.1f}%' if p > 0 else '',
        colors=['#4CAF50', '#FFC107'],
        startangle=90
    )
    plt.title('Görev Tamamlama Durumu')
    plt.tight_layout()
    return generate_plot_image(plt)

def generate_timeline_chart(user):
    """Zaman içinde görev tamamlama grafiği"""
    # Son 30 günlük veri
    # 'completed_date' yerine 'completed_at' kullanıyoruz
    timeline_data = (
        Task.objects
        .filter(user=user, status='completed', completed_at__isnull=False)
        .annotate(date=TruncDate('completed_at'))
        .values('date')
        .annotate(count=Count('id'))
        .order_by('date')[:30]  # Son 30 gün
    )
    
    if not timeline_data:
        # Veri yoksa boş grafik oluştur
        plt.figure(figsize=(10, 4))
        plt.title('Günlere Göre Tamamlanan Görevler')
        plt.xlabel('Tarih')
        plt.ylabel('Tamamlanan Görev Sayısı')
        plt.text(0.5, 0.5, 'Veri Yok', ha='center', va='center')
        return generate_plot_image(plt)
    
    dates = [d['date'].strftime('%Y-%m-%d') for d in timeline_data]
    counts = [d['count'] for d in timeline_data]
    
    plt.figure(figsize=(10, 4))
    sns.lineplot(x=dates, y=counts, marker='o', color='#2196F3')
    plt.title('Günlere Göre Tamamlanan Görevler')
    plt.xlabel('Tarih')
    plt.ylabel('Tamamlanan Görev Sayısı')
    plt.xticks(rotation=45)
    plt.tight_layout()
    return generate_plot_image(plt)


def generate_productivity_chart(user, start_date, end_date):
    """Haftalık verimlilik eğrisi oluşturur"""
    dates = []
    scores = []
    
    current_date = start_date
    while current_date <= end_date:
        next_date = current_date + timedelta(days=7)
        completed = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date__gte=current_date,
            completed_at__date__lt=next_date
        ).count()
        
        total = Task.objects.filter(
            user=user,
            created_at__date__lt=next_date
        ).count()
        
        score = (completed / total * 100) if total > 0 else 0
        dates.append(current_date.strftime('%d %b'))
        scores.append(round(score, 1))
        current_date = next_date
    
    plt.figure(figsize=(10, 4))
    sns.lineplot(x=dates, y=scores, marker='o', color='#9C27B0')
    plt.axhline(y=np.mean(scores), color='#FF5722', linestyle='--', label='Ortalama')
    plt.fill_between(dates, scores, alpha=0.2, color='#9C27B0')
    plt.title('Haftalık Verimlilik Eğrisi')
    plt.xlabel('Tarih')
    plt.ylabel('Verimlilik Skoru')
    plt.xticks(rotation=45)
    plt.legend()
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
    """7 günlük veri trendleri"""
    dates = [(datetime.now() - timedelta(days=i)).date() for i in range(6, -1, -1)]
    
    daily_data = []
    for day in dates:
        completed = Task.objects.filter(
            user=user,
            status='completed',
            completed_at__date=day
        ).count()
        
        created = Task.objects.filter(
            user=user,
            created_at__date=day
        ).count()
        
        daily_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'day_name': day.strftime('%A'),
            'completed': completed,
            'created': created,
            'efficiency': (completed / created * 100) if created > 0 else 0
        })
    
    return daily_data

def generate_daily_heatmap(user):
    """Günlük aktivite heatmap"""
    # 12 haftalık veri
    data = Task.objects.filter(
        user=user,
        created_at__gte=datetime.now() - timedelta(weeks=12)
    ).annotate(
        week=ExtractWeekDay('created_at'),
        day=F('created_at__week_day')
    ).values('week', 'day').annotate(count=Count('id'))
    
    # Heatmap veri hazırlama
    # ... (heatmap oluşturma kodu)
    
    return generate_plot_image(plt)