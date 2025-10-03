from django.urls import path
from . import views
from .views import HelpView, FAQView, SupportView, GuideView, ContactView, PrivacyView, TermsView, CookiesView, LicenseView

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('home/', views.home, name='home'),
    path('pomodoro/', views.pomodoro_view, name='pomodoro'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/event/create/', views.create_calendar_event, name='create_calendar_event'),
    path('calendar/events/', views.get_calendar_events, name='calendar_events'),  # BU SATIR EKLENDİ
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_detail_view, name='day_detail'),
    path('calendar/event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('calendar/event/<int:event_id>/json/', views.event_detail_json, name='event_detail_json'),
    path('pomodoro/save-session/', views.save_pomodoro_session, name='save_pomodoro_session'),
    path('calendar/events/', views.get_calendar_events, name='get_calendar_events'),

    
    # Static pages
    path('help/', HelpView.as_view(), name='help'),
    path('faq/', FAQView.as_view(), name='faq'),
    path('support/', SupportView.as_view(), name='support'),
    path('guide/', GuideView.as_view(), name='guide'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('privacy/', PrivacyView.as_view(), name='privacy'),
    path('terms/', TermsView.as_view(), name='terms'),
    path('cookies/', CookiesView.as_view(), name='cookies'),
    path('license/', LicenseView.as_view(), name='license'),
    
]