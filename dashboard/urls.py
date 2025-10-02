# dashboard/urls.py
from django.urls import path
from . import views
from .views import HelpView, FAQView, SupportView, GuideView, ContactView, PrivacyView, TermsView, CookiesView, LicenseView

app_name = 'dashboard'

urlpatterns = [
    path('', views.landing_page, name='landing'),  # Ana sayfa artık landing page
    path('home/', views.home, name='home'),
    path('pomodoro/', views.pomodoro_view, name='pomodoro'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('calendar/event/create/', views.create_calendar_event, name='create_calendar_event'),
    path('calendar/events/', views.get_calendar_events, name='calendar_events'),
    path('calendar/<int:year>/<int:month>/<int:day>/', views.day_detail_view, name='day_detail'),
    path('calendar/event/<int:event_id>/', views.event_detail_view, name='event_detail'),
    path('pomodoro/save-session/', views.save_pomodoro_session, name='save_pomodoro_session'),
    # Yeni eklenen sayfalar
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