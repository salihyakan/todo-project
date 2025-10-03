from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.analytics_dashboard, name='dashboard'),
    path('refresh/', views.refresh_analytics, name='refresh'),  # BU SATIR EKLENDİ
]