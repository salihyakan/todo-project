from django.contrib import admin
from .models import Note, Category

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'priority', 'is_pinned', 'created_at')
    list_filter = ('priority', 'is_pinned', 'category', 'user')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    list_editable = ('is_pinned',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'slug')
    list_filter = ('user',)
    search_fields = ('name',)