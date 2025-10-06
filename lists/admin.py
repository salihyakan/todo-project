from django.contrib import admin
from .models import List, ListItem

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'list_type', 'is_pinned', 'created_at', 'progress_percentage']
    list_filter = ['list_type', 'is_pinned', 'created_at']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        ('Temel Bilgiler', {
            'fields': ['user', 'title', 'description', 'list_type']
        }),
        ('Görünüm', {
            'fields': ['color', 'is_pinned']
        }),
        ('Zaman Damgaları', {
            'fields': ['created_at', 'updated_at'],
            'classes': ['collapse']
        }),
    ]

@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ['content', 'list', 'completed', 'priority', 'due_date', 'created_at']
    list_filter = ['completed', 'priority', 'created_at']
    search_fields = ['content', 'list__title']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['completed', 'priority']