from django.contrib import admin
from tinymce.widgets import TinyMCE
from .models import StudyNote
from .forms import StudyNoteForm

@admin.register(StudyNote)
class StudyNoteAdmin(admin.ModelAdmin):
    form = StudyNoteForm
    list_display = ['title', 'user', 'created_at', 'updated_at']
    list_filter = ['created_at', 'user']
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'