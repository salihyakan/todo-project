from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Note, Category
from .forms import NoteForm, CategoryForm
from django.db.models import Q

@login_required
def note_list(request):
    # Filtreleme ve arama parametreleri
    query = request.GET.get('q')
    category_slug = request.GET.get('category')
    is_pinned = request.GET.get('pinned')
    task_id = request.GET.get('task')
    date_filter = request.GET.get('date', '')
    
    # select_related ile optimizasyon
    notes = Note.objects.filter(user=request.user).select_related('category', 'task')
    
    # Arama
    if query:
        notes = notes.filter(Q(title__icontains=query) | Q(content__icontains=query))
    
    # Kategori filtresi
    if category_slug:
        try:
            category = Category.objects.get(slug=category_slug, user=request.user)
            notes = notes.filter(category=category)
        except Category.DoesNotExist:
            pass
    
    # Görev filtresi - tür dönüşümü yap
    current_task_id = None
    if task_id and task_id != 'none':
        try:
            current_task_id = int(task_id)
            from todo.models import Task
            task = get_object_or_404(Task, id=current_task_id, user=request.user)
            notes = notes.filter(task=task)
        except (ValueError, Task.DoesNotExist):
            pass
    elif task_id == 'none':
        # Görevsiz notlar
        notes = notes.filter(task__isnull=True)
    
    # Tarih filtresi
    if date_filter:
        try:
            from datetime import datetime
            filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            notes = notes.filter(created_at__date=filter_date)
        except ValueError:
            pass
    
    # Sabitlenmiş notlar
    if is_pinned == 'true':
        notes = notes.filter(is_pinned=True)
    
    # Kategorileri getir (kenar çubuğu için) - optimizasyon: sadece gerekli alanlar
    categories = Category.objects.filter(user=request.user).only('id', 'name', 'slug', 'color')
    
    # Görevleri getir (filtreleme için) - optimizasyon: sadece gerekli alanlar
    from todo.models import Task
    tasks = Task.objects.filter(user=request.user).only('id', 'title')
    
    # İstatistikleri hesapla
    total_notes_count = notes.count()
    pinned_notes_count = notes.filter(is_pinned=True).count()
    task_notes_count = notes.filter(task__isnull=False).count()
    
    # Sonuçları tarihe göre sırala
    notes = notes.order_by('-is_pinned', '-updated_at')
    
    context = {
        'notes': notes,
        'categories': categories,
        'tasks': tasks,
        'current_category': category_slug,
        'current_task': task_id,
        'current_task_id': current_task_id,
        'is_pinned': is_pinned,
        'query': query,
        'date_filter': date_filter,
        'total_notes_count': total_notes_count,
        'pinned_notes_count': pinned_notes_count,
        'task_notes_count': task_notes_count,
    }
    
    return render(request, 'notes/note_list.html', context)

@login_required
def note_detail(request, pk):
    # select_related ile optimizasyon
    note = get_object_or_404(
        Note.objects.select_related('category', 'task'), 
        pk=pk, 
        user=request.user
    )
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
def note_create(request):
    categories = Category.objects.filter(user=request.user).only('id', 'name', 'color')
    from todo.models import Task
    tasks = Task.objects.filter(user=request.user).only('id', 'title')
    
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            messages.success(request, 'Not başarıyla oluşturuldu!')
            return redirect('notes:note_list')
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = NoteForm(request.user)
    
    return render(request, 'notes/note_form.html', {
        'form': form,
        'categories': categories,
        'tasks': tasks
    })

@login_required
def note_update(request, pk):
    # select_related ile optimizasyon
    note = get_object_or_404(
        Note.objects.select_related('category', 'task'), 
        pk=pk, 
        user=request.user
    )
    categories = Category.objects.filter(user=request.user).only('id', 'name', 'color')
    from todo.models import Task
    tasks = Task.objects.filter(user=request.user).only('id', 'title')
    
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST, instance=note)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, 'Not başarıyla güncellendi!')
                
                # Eğer bir görevle ilişkiliyse, görev detay sayfasına yönlendir
                if note.task:
                    return redirect('todo:task_detail', pk=note.task.id)
                return redirect('notes:note_detail', pk=note.pk)
            except Exception as e:
                # Redis hatasını yakala ve devam et
                messages.success(request, 'Not başarıyla güncellendi! (Bildirim gönderilemedi)')
                if note.task:
                    return redirect('todo:task_detail', pk=note.task.id)
                return redirect('notes:note_detail', pk=note.pk)
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # GET isteğinde formu mevcut not verileriyle doldur
        form = NoteForm(request.user, instance=note)
    
    return render(request, 'notes/note_form.html', {
        'form': form,
        'note': note,
        'categories': categories,
        'tasks': tasks,
        'is_update': True  # Güncelleme modunda olduğumuzu belirt
    })

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        task_id = note.task.id if note.task else None
        note.delete()
        messages.success(request, 'Not başarıyla silindi!')
        
        # Eğer bir görevle ilişkiliyse, görev detay sayfasına yönlendir
        if task_id:
            return redirect('todo:task_detail', pk=task_id)
        return redirect('notes:note_list')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
def note_create_for_task(request, task_id):
    """Belirli bir task için not oluştur"""
    from todo.models import Task
    task = get_object_or_404(Task, id=task_id, user=request.user)
    categories = Category.objects.filter(user=request.user).only('id', 'name', 'color')
    
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.task = task  # Görev ilişkisini zorla
            note.save()
            messages.success(request, 'Not başarıyla oluşturuldu!')
            return redirect('todo:task_detail', pk=task.id)
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = NoteForm(request.user, initial={'task': task})
    
    return render(request, 'notes/note_form.html', {
        'form': form,
        'categories': categories,
        'task': task,
        'title': f'"{task.title}" için Not Ekle'
    })

@login_required
def task_notes(request, task_id):
    """Bir task'a ait notları listele"""
    from todo.models import Task
    task = get_object_or_404(Task, id=task_id, user=request.user)
    # select_related ile optimizasyon
    notes = Note.objects.filter(task=task, user=request.user).select_related('category').order_by('-is_pinned', '-updated_at')
    
    return render(request, 'notes/task_notes.html', {
        'task': task,
        'notes': notes
    })

@login_required
def category_list(request):
    # Sadece gerekli alanları seçerek optimizasyon
    categories = Category.objects.filter(user=request.user).only('id', 'name', 'slug', 'color')
    return render(request, 'notes/category_list.html', {'categories': categories})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            messages.success(request, 'Kategori başarıyla oluşturuldu!')
            return redirect('notes:category_list')
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CategoryForm()
    
    return render(request, 'notes/category_form.html', {'form': form})

@login_required
def category_update(request, slug):
    category = get_object_or_404(Category, slug=slug, user=request.user)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Kategori başarıyla güncellendi!')
            return redirect('notes:category_list')
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'notes/category_form.html', {'form': form, 'category': category})

@login_required
def category_delete(request, slug):
    category = get_object_or_404(Category, slug=slug, user=request.user)
    if request.method == 'POST':
        category.delete()
        messages.success(request, 'Kategori başarıyla silindi!')
        return redirect('notes:category_list')
    return render(request, 'notes/category_confirm_delete.html', {'category': category})