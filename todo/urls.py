from django.urls import path
from . import views

app_name = 'todo'

urlpatterns = [
    path('', views.task_list, name='task_list'),
    path('create/', views.task_create, name='task_create'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    path('<int:pk>/update/', views.task_update, name='task_update'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('<int:pk>/update-status/', views.update_task_status, name='update_task_status'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('categories/<slug:slug>/update/', views.category_update, name='category_update'),
    path('categories/<slug:slug>/delete/', views.category_delete, name='category_delete'),

    path('<int:pk>/complete/', views.complete_task, name='complete_task'),
]