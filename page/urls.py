from django.urls import path
from .views import (
    home_page_view, 
    task_add_view, 
    tasks_view, 
    calendar_view,
)

app_name = 'page'

urlpatterns = [
    path('home-page/', home_page_view, name='home_page_view'),
    path('task-add/', task_add_view, name='task_add_view'),
    path("tasks/", tasks_view, name='tasks_view'),
    path("calendar/", calendar_view, name='calendar_view'),
]