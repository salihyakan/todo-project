from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Task, Category
from user_profile.models import Badge, UserBadge
from .forms import TaskForm, CategoryForm
from django.utils import timezone
from django.http import JsonResponse
from datetime import datetime

@login_required
def task_list(request):
    # Filtreleme parametreleri
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-due_date')
    due_date = request.GET.get('due_date', '')
    
    # Temel sorgu - süresi geçmiş görevleri varsayılan olarak gösterme
    tasks = Task.objects.filter(user=request.user)
    
    # Özel durum filtreleri (hızlı filtre butonları)
    quick_filter = request.GET.get('filter', '')
    if quick_filter:
        if quick_filter == 'active':
            tasks = tasks.filter(status__in=['todo', 'in_progress'])
        elif quick_filter == 'completed':
            tasks = tasks.filter(status='completed')
        elif quick_filter == 'overdue':
            tasks = Task.objects.filter(user=request.user, status='overdue')
        elif quick_filter == 'today':
            today = timezone.now().date()
            tasks = tasks.filter(due_date__date=today)
    
    # Detaylı filtreleme
    if category_id:
        tasks = tasks.filter(category__id=category_id)
    if status:
        tasks = tasks.filter(status=status)
    if priority:
        tasks = tasks.filter(priority=priority)
    if search:
        tasks = tasks.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search)
        )
    if due_date:
        try:
            filter_date = datetime.datetime.strptime(due_date, '%Y-%m-%d').date()
            tasks = tasks.filter(due_date__date=filter_date)
        except ValueError:
            pass
    
    # Sıralama
    tasks = tasks.order_by(sort)
    
    # Sayfalama
    paginator = Paginator(tasks, 9)  # 3x3 grid için 9 görev
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_category': category_id,
        'current_status': status,
        'current_priority': priority,
        'current_search': search,
        'current_sort': sort,
        'current_due_date': due_date,
        'current_filter': quick_filter,
        'has_filters': any([category_id, status, priority, search, due_date, quick_filter])
    }
    
    return render(request, 'todo/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Görev başarıyla oluşturuldu!')
            return redirect('todo:task_list')
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        initial = {}
        category_id = request.GET.get('category')
        if category_id:
            try:
                category = Category.objects.get(id=category_id, user=request.user)
                initial['category'] = category
            except Category.DoesNotExist:
                pass
        
        form = TaskForm(user=request.user, initial=initial)
    
    return render(request, 'todo/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            if form.cleaned_data['status'] == 'completed' and task.status != 'completed':
                task.completed_at = timezone.now()
            elif form.cleaned_data['status'] != 'completed' and task.completed_at:
                task.completed_at = None
            
            form.save()
            messages.success(request, 'Görev başarıyla güncellendi!')
            return redirect('todo:task_detail', pk=task.pk)
        else:
            messages.error(request, 'Lütfen formdaki hataları düzeltin.')
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'todo/task_form.html', {'form': form, 'task': task})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    # Notes app'inden task ile ilişkili notları al
    from notes.models import Note
    notes = Note.objects.filter(task=task, user=request.user).order_by('-is_pinned', '-updated_at')[:3]  # Son 3 not
    
    return render(request, 'todo/task_detail.html', {
        'task': task,
        'notes': notes
    })

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        try:
            task_title = task.title
            task.delete()
            messages.success(request, f'"{task_title}" görevi başarıyla silindi!')
            return redirect('todo:task_list')
        except Exception as e:
            messages.error(request, f'Görev silinirken hata oluştu: {str(e)}')
            return redirect('todo:task_list')
    
    return render(request, 'todo/task_confirm_delete.html', {'task': task})

@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    
    if request.method == 'POST' and request.is_ajax():
        new_status = request.POST.get('status')
        
        if new_status in ['todo', 'in_progress', 'completed']:
            task.status = new_status
            
            # Tamamlandı durumunda tamamlanma tarihini güncelle
            if new_status == 'completed' and task.status != 'completed':
                task.completed_at = timezone.now()
                check_and_award_badges(request.user)
            
            task.save()
            return JsonResponse({'success': True, 'status': task.get_status_display()})
    
    return JsonResponse({'success': False}, status=400)

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user).order_by('name')
    return render(request, 'todo/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, user=request.user)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Kategori başarıyla oluşturuldu!')
            return redirect('todo:category_list')
    else:
        form = CategoryForm(user=request.user)
    
    return render(request, 'todo/category_form.html', {'form': form})

@login_required
def category_update(request, slug):
    category = get_object_or_404(Category, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori başarıyla güncellendi!')
            return redirect('todo:category_list')
    else:
        form = CategoryForm(instance=category, user=request.user)
    
    return render(request, 'todo/category_form.html', {'form': form, 'category': category})

@login_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug, user=request.user)
    if request.method == 'POST':
        # Kategorinin kullanıldığı görevleri kontrol et
        if Task.objects.filter(category=category).exists():
            messages.warning(request, 'Bu kategori kullanılmakta olduğu için silinemez!')
            return redirect('todo:category_list')
        
        category.delete()
        messages.success(request, 'Kategori başarıyla silindi!')
        return redirect('todo:category_list')
    return render(request, 'todo/category_confirm_delete.html', {'category': category})

@login_required
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, user=request.user)
    tasks = Task.objects.filter(user=request.user, category=category).order_by('-due_date')
    return render(request, 'todo/category_detail.html', {
        'category': category,
        'tasks': tasks
    })

def check_and_award_badges(user):
    # Bu fonksiyon görev tamamlandığında rozet kontrolü yapar
    completed_tasks = Task.objects.filter(user=user, status='completed').count()
    
    # Örnek rozet kazanma mantığı
    badges_to_award = []
    if completed_tasks >= 10:
        badges_to_award.append(Badge.objects.get_or_create(
            name='Usta Planlayıcı',
            defaults={
                'description': '10 görev tamamlama başarısı',
                'icon': 'fas fa-crown'
            }
        )[0])
    
    # Kullanıcıya rozetleri ata
    for badge in badges_to_award:
        UserBadge.objects.get_or_create(user=user, badge=badge)

@login_required
def complete_task(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.status = 'completed'
        task.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'status': task.get_status_display(),
                'completed_at': task.completed_at.strftime('%d.%m.%Y %H:%M')
            })
        messages.success(request, 'Görev tamamlandı olarak işaretlendi!')
        return redirect('todo:task_detail', pk=task.pk)
    return JsonResponse({'success': False}, status=400)
