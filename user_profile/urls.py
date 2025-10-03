from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'user_profile'

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/view/', views.profile_view, name='profile_view'),  # BU SATIR EKLENDİ
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    
    # Password management
    path('password_change/', views.CustomPasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Badges
    path('badges/check/', views.force_badge_check, name='force_badge_check'),  # ÖNCE
    path('badges/<slug:slug>/', views.badge_detail, name='badge_detail'),      # SONRA
    path('badges/', views.badge_list, name='badge_list'),    
    
    # Notifications
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/clear/', views.clear_history_notifications, name='clear_history_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),  # BU SATIR EKLENDİ
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/check-new/', views.check_new_notifications, name='check_new_notifications'),  # BU SATIR EKLENDİ
    
    # Settings
    path('update_pomodoro/', views.update_pomodoro, name='update_pomodoro'),
]