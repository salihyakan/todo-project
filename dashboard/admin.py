from django.contrib import admin
from .models import DashboardStats, CalendarEvent, PomodoroSession

@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_updated', 'tasks_completed', 'pomodoros_completed', 'notes_created', 'current_streak')
    search_fields = ('user__username',)
    list_filter = ('last_updated', 'created_at')
    readonly_fields = ('last_updated',)

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'event_type', 'is_all_day')
    list_filter = ('event_type', 'user', 'is_all_day')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)

@admin.register(PomodoroSession)
class PomodoroSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_type', 'duration', 'completed', 'created_at']
    list_filter = ['session_type', 'completed', 'created_at']
    search_fields = ['user__username']
    date_hierarchy = 'created_at'