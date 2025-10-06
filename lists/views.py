from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.db import models
from .models import List, ListItem
from .forms import ListForm, ListItemForm, QuickAddItemForm

class ListListView(LoginRequiredMixin, ListView):
    model = List
    template_name = 'lists/list_list.html'
    context_object_name = 'lists'
    
    def get_queryset(self):
        queryset = List.objects.filter(user=self.request.user)
        list_type = self.request.GET.get('type')
        if list_type and list_type != 'all':
            queryset = queryset.filter(list_type=list_type)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_types'] = dict(List.LIST_TYPES)
        context['current_type'] = self.request.GET.get('type', 'all')
        return context

class ListDetailView(LoginRequiredMixin, DetailView):
    model = List
    template_name = 'lists/list_detail.html'
    context_object_name = 'list_obj'
    
    def get_queryset(self):
        return List.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item_form'] = ListItemForm()
        context['quick_form'] = QuickAddItemForm()
        context['completed_items'] = self.object.items.filter(completed=True).order_by('-updated_at')
        context['pending_items'] = self.object.items.filter(completed=False).order_by('-updated_at')
        return context

class ListCreateView(LoginRequiredMixin, CreateView):
    model = List
    form_class = ListForm
    template_name = 'lists/list_form.html'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Liste başarıyla oluşturuldu!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('lists:list_detail', kwargs={'pk': self.object.pk})

class ListUpdateView(LoginRequiredMixin, UpdateView):
    model = List
    form_class = ListForm
    template_name = 'lists/list_form.html'
    
    def get_queryset(self):
        return List.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse_lazy('lists:list_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Liste başarıyla güncellendi!')
        return super().form_valid(form)

class ListDeleteView(LoginRequiredMixin, DeleteView):
    model = List
    template_name = 'lists/list_confirm_delete.html'
    success_url = reverse_lazy('lists:list_list')
    
    def get_queryset(self):
        return List.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Liste başarıyla silindi!')
        return super().form_valid(form)

@login_required
def toggle_item_status(request, item_id):
    """Madde tamamlama durumunu değiştir - DEBUG EKLİ"""
    print(f"🎯 TOGGLE İSTEĞİ GELDİ - item_id: {item_id}, Kullanıcı: {request.user}, Method: {request.method}")
    
    if request.method == 'POST':
        try:
            item = get_object_or_404(ListItem, id=item_id, list__user=request.user)
            print(f"🎯 Madde bulundu: {item.content}, Mevcut durum: {item.completed}")
            
            item.completed = not item.completed
            item.updated_at = timezone.now()
            item.save()
            
            # Listeyi güncelle
            list_obj = item.list
            list_obj.updated_at = timezone.now()
            list_obj.save()
            
            print(f"🎯 Toggle başarılı. Yeni durum: {item.completed}")
            
            return JsonResponse({
                'success': True,
                'completed': item.completed,
                'progress': list_obj.progress_percentage(),
                'completed_count': list_obj.completed_items_count(),
                'total_count': list_obj.total_items_count()
            })
        except Exception as e:
            print(f"🎯 Toggle hatası: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    print("🎯 Toggle: Geçersiz method")
    return JsonResponse({'success': False, 'error': 'Sadece POST methodu kabul edilir'})

@login_required
def add_item(request, list_id):
    """Yeni madde ekle - BASİT ve GÜVENLİ"""
    print(f"Add item isteği geldi: {list_id}")  # Debug
    list_obj = get_object_or_404(List, id=list_id, user=request.user)
    
    if request.method == 'POST':
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        # Hızlı ekleme formu - sadece content alanı var
        if 'content' in request.POST and not any(key in request.POST for key in ['priority', 'due_date']):
            form = QuickAddItemForm(request.POST)
        else:
            form = ListItemForm(request.POST)
            
        if form.is_valid():
            item = form.save(commit=False)
            item.list = list_obj
            
            # Order değerini ayarla
            max_order = ListItem.objects.filter(list=list_obj).aggregate(
                models.Max('order')
            )['order__max'] or 0
            item.order = max_order + 1
            
            item.save()
            
            # Listeyi güncelle
            list_obj.updated_at = timezone.now()
            list_obj.save()
            
            print(f"Add item başarılı: {item.id}")  # Debug
            
            if is_ajax:
                return JsonResponse({
                    'success': True,
                    'item_id': item.id,
                    'content': item.content
                })
            
            messages.success(request, 'Madde başarıyla eklendi!')
            return redirect('lists:list_detail', pk=list_id)
        else:
            print(f"Add item form hatası: {form.errors}")  # Debug
            if is_ajax:
                return JsonResponse({
                    'success': False, 
                    'errors': form.errors.as_json()
                })
            messages.error(request, 'Formda hatalar var!')
    
    return redirect('lists:list_detail', pk=list_id)

@login_required
def delete_item(request, item_id):
    """Madde sil - DEBUG EKLİ"""
    print(f"🗑️ DELETE İSTEĞİ GELDİ - item_id: {item_id}, Kullanıcı: {request.user}, Method: {request.method}")
    
    if request.method == 'POST':
        try:
            item = get_object_or_404(ListItem, id=item_id, list__user=request.user)
            print(f"🗑️ Silinecek madde: {item.content}")
            
            list_obj = item.list
            item.delete()
            
            # Listeyi güncelle
            list_obj.updated_at = timezone.now()
            list_obj.save()
            
            print(f"🗑️ Delete başarılı")
            
            return JsonResponse({
                'success': True,
                'progress': list_obj.progress_percentage(),
                'completed_count': list_obj.completed_items_count(),
                'total_count': list_obj.total_items_count()
            })
        except Exception as e:
            print(f"🗑️ Delete hatası: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    print("🗑️ Delete: Geçersiz method")
    return JsonResponse({'success': False, 'error': 'Sadece POST methodu kabul edilir'})