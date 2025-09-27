from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tools_home, name='home'),
    path('calculator/', views.calculator, name='calculator'),
    path('stopwatch/', views.stopwatch, name='stopwatch'),
    path('timer/', views.timer, name='timer'),
]