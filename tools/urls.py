from django.urls import path
from . import views

app_name = 'tools'

urlpatterns = [
    path('', views.tools_home, name='home'),
    path('calculator/', views.calculator, name='calculator'),
    path('stopwatch/', views.stopwatch, name='stopwatch'),
    path('timer/', views.timer, name='timer'),
    # Çalışma Notları URL'leri
    path('study-notes/', views.StudyNoteListView.as_view(), name='study_notes_list'),
    path('study-notes/new/', views.StudyNoteCreateView.as_view(), name='study_note_create'),
    path('study-notes/<int:pk>/', views.StudyNoteDetailView.as_view(), name='study_note_detail'),  # Yeni ekle
    path('study-notes/<int:pk>/edit/', views.StudyNoteUpdateView.as_view(), name='study_note_update'),
    path('study-notes/<int:pk>/delete/', views.StudyNoteDeleteView.as_view(), name='study_note_delete'),
]