from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('<int:pk>/', views.note_detail, name='note_detail'),
    path('<int:pk>/update/', views.note_update, name='note_update'),
    path('<int:pk>/delete/', views.note_delete, name='note_delete'),    
    path('create/', views.note_create, name='note_create'),
    
    # Todo entegrasyonu için yeni URL'ler
    path('task/<int:task_id>/', views.task_notes, name='task_notes'),
    path('task/<int:task_id>/create/', views.note_create_for_task, name='note_create_for_task'),
    
    # Kategori URL'leri
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<slug:slug>/update/', views.category_update, name='category_update'),
    path('categories/<slug:slug>/delete/', views.category_delete, name='category_delete'),
]