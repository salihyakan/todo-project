"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from page.views import (
    home_page_view, 
    user_home_page_view, 
    user_task_add_view, 
    tasks_view, 
    calendar_view,
)



urlpatterns = [
    path('', home_page_view, name='home_page_view'),
    path('home-page', home_page_view, name='home_page_view'),
    path('admin/', admin.site.urls),
    path('user-home-page/', user_home_page_view, name='user_home_page_view'),
    path('user-task-add/', user_task_add_view, name='user_task_add_view'),
    path("tasks/", tasks_view, name='tasks_view'),
    path("calendar/", calendar_view, name='calendar_view')
]





