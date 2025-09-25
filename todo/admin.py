from django.contrib import admin
from .models import Task, Note, Category
from user_profile.models import Badge, UserBadge

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'color', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)
    readonly_fields = ('slug', 'created_at', 'updated_at')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'category', 'due_date', 'priority', 'status')
    list_filter = ('priority', 'status', 'user', 'category')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('content', 'user', 'task', 'created_at')
    search_fields = ('content',)
