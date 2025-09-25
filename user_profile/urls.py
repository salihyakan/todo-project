from django.urls import path
from . import views
from .views import (
    CustomPasswordResetView, CustomPasswordResetDoneView, 
    CustomPasswordResetConfirmView, CustomPasswordResetCompleteView
)

app_name = 'user_profile'

urlpatterns = [
    path('', views.profile, name='profile'),  # /profile/ için ana sayfa
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    # path('profile/', ...) kaldırıldı çünkü zaten ana URL bu
    
    # Şifre sıfırlama URL'leri
    path('password_reset/', CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    path('update_pomodoro/', views.update_pomodoro, name='update_pomodoro'),
    path('badges/', views.badge_list, name='badge_list'),
    path('badges/<slug:slug>/', views.badge_detail, name='badge_detail'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', 
         views.mark_notification_as_read, name='mark_notification_as_read'),
    path('notifications/mark-all-read/', 
         views.mark_all_notifications_read, name='mark_all_notifications_read'),
]