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
    
    notes = Note.objects.filter(user=request.user)
    
    # Arama
    if query:
        notes = notes.filter(Q(title__icontains=query) | Q(content__icontains=query))
    
    # Kategori filtresi
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug, user=request.user)
        notes = notes.filter(category=category)
    
    # Sabitlenmiş notlar
    if is_pinned == 'true':
        notes = notes.filter(is_pinned=True)
    
    # Kategorileri getir (kenar çubuğu için)
    categories = Category.objects.filter(user=request.user)
    
    # Sonuçları tarihe göre sırala
    notes = notes.order_by('-is_pinned', '-updated_at')
    
    context = {
        'notes': notes,
        'categories': categories,
        'current_category': category_slug,
        'is_pinned': is_pinned,
        'query': query
    }
    
    return render(request, 'notes/note_list.html', context)

@login_required
def note_detail(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    return render(request, 'notes/note_detail.html', {'note': note})

@login_required
def note_create(request):
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        try:
            # Form verilerini doğrudan al
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            category_id = request.POST.get('category')
            
            # Gerekli alan kontrolü
            if not title or not content:
                raise ValueError("Başlık ve içerik zorunlu alanlardır")
            
            # Kategori kontrolü
            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=int(category_id), user=request.user)
                except (Category.DoesNotExist, ValueError):
                    messages.warning(request, 'Geçersiz kategori seçildi')
            
            # Notu oluştur
            note = Note.objects.create(
                user=request.user,
                title=title,
                content=content,
                category=category,
                priority=request.POST.get('priority', 'M'),
                is_pinned=bool(request.POST.get('is_pinned', False)),
                related_date=request.POST.get('related_date') or None
            )
            
            messages.success(request, 'Not başarıyla oluşturuldu!')
            return redirect('notes:note_list')  # Kesinlikle listeye yönlendir
            
        except Exception as e:
            messages.error(request, f'Hata: {str(e)}')
            return render(request, 'notes/note_form.html', {
                'categories': categories,
                'title': request.POST.get('title', ''),
                'content': request.POST.get('content', ''),
                'priority': request.POST.get('priority', 'M'),
                'is_pinned': bool(request.POST.get('is_pinned', False)),
                'related_date': request.POST.get('related_date', '')
            })
    
    # GET isteği için
    return render(request, 'notes/note_form.html', {'categories': categories})

@login_required
def note_update(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    categories = Category.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = NoteForm(request.user, request.POST, instance=note)
        if form.is_valid():
            form.save()
            messages.success(request, 'Not başarıyla güncellendi!')
            return redirect('notes:note_detail', pk=note.pk)
    else:
        form = NoteForm(request.user, instance=note)
    
    return render(request, 'notes/note_form.html', {
        'form': form,
        'note': note,
        'categories': categories
    })

@login_required
def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk, user=request.user)
    if request.method == 'POST':
        note.delete()
        messages.success(request, 'Not başarıyla silindi!')
        return redirect('notes:note_list')
    return render(request, 'notes/note_confirm_delete.html', {'note': note})

@login_required
def category_list(request):
    categories = Category.objects.filter(user=request.user)
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