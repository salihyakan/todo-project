from django.contrib import admin
from django.urls import path, include
from page.views import home_view
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home_view'),
    path('home', home_view, name='home_view'),
    # USER
    path('user/', include('user_profile.urls' , namespace='user')),
    # PAGE
    path('page/', include('page.urls' , namespace='page')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)





