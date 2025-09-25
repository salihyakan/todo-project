# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView  



urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')), # Ana sayfa için
    path('todo/', include('todo.urls', namespace='todo')),
    path('profile/', include('user_profile.urls', namespace='user_profile')),
    path('notes/', include('notes.urls', namespace='notes')),
    path('analytics/', include('analytics.urls', namespace='analytics')),  # Namespace eklendi
    path('favicon.ico', RedirectView.as_view(url=settings.STATIC_URL + 'favicon.ico')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Static dosyalar için