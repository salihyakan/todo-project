from django.contrib import admin
from .models import Note, Category

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'task', 'category', 'priority', 'is_pinned', 'created_at']
    list_filter = ['priority', 'is_pinned', 'category', 'created_at']
    search_fields = ['title', 'content']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'color', 'slug']
    list_filter = []  # created_at alanı olmadığı için boş bırakıyoruz
    search_fields = ['name']
    prepopulated_fields = {'slug': ('name',)}