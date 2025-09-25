from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Task, Note, Category
from user_profile.models import Badge, UserBadge
from .forms import TaskForm, NoteForm, CategoryForm
from django.utils import timezone
from django.http import JsonResponse

@login_required
def task_list(request):
    # Filtreleme parametreleri
    category_id = request.GET.get('category', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', '-due_date')
    
    # Temel sorgu
    tasks = Task.objects.filter(user=request.user)
    
    # Filtreleme
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
    
    # Sıralama
    tasks = tasks.order_by(sort)
    
    # Sayfalama
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Context verileri
    context = {
        'page_obj': page_obj,
        'status_choices': Task.STATUS_CHOICES,
        'priority_choices': Task.PRIORITY_CHOICES,
        'current_category': category_id,
        'current_status': status,
        'current_priority': priority,
        'current_search': search,
        'current_sort': sort,
        'has_filters': any([category_id, status, priority, search])
    }
    
    return render(request, 'todo/task_list.html', context)


@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.status = 'todo'  # Varsayılan olarak 'todo' olarak ayarla
            task.save()
            messages.success(request, 'Görev başarıyla oluşturuldu!')
            return redirect('todo:task_list')
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
            # Görev durumu değiştiyse
            if form.cleaned_data['status'] == 'completed' and task.status != 'completed':
                task.completed_at = timezone.now()
            elif form.cleaned_data['status'] != 'completed' and task.completed_at:
                task.completed_at = None
            
            form.save()
            messages.success(request, 'Görev başarıyla güncellendi!')
            return redirect('todo:task_detail', pk=task.pk)
    else:
        form = TaskForm(instance=task, user=request.user)
    
    return render(request, 'todo/task_form.html', {'form': form, 'task': task})

@login_required
def task_detail(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    notes = task.notes.all()
    
    if request.method == 'POST':
        note_form = NoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.user = request.user
            note.task = task
            note.save()
            messages.success(request, 'Not başarıyla eklendi!')
            return redirect('todo:task_detail', pk=task.pk)
    else:
        note_form = NoteForm()
    
    return render(request, 'todo/task_detail.html', {
        'task': task,
        'notes': notes,
        'note_form': note_form
    })


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Görev başarıyla silindi!')
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