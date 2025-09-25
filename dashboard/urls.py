from django.urls import path
from . import views

app_name = 'dashboard'  

urlpatterns = [
    path('', views.home, name='home'),
    path('pomodoro/', views.pomodoro_view, name='pomodoro'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/events/', views.get_calendar_events, name='calendar_events'),
    path('calendar/events/create/', views.create_calendar_event, name='create_calendar_event'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_detail_view, name='day_detail'),
    path('calendar/event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('save-pomodoro-session/', views.save_pomodoro_session, name='save_pomodoro_session'),
    path('calendar/event/<int:event_id>/json/', views.event_detail_json, name='event_detail_json'),
]