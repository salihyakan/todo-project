from django.contrib import admin
from .models import DashboardStats, CalendarEvent

@admin.register(DashboardStats)
class DashboardStatsAdmin(admin.ModelAdmin):
    list_display = ('user', 'last_login', 'tasks_completed', 'pomodoros_completed', 'notes_created')
    search_fields = ('user__username',)
    list_filter = ('last_login',)

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_date', 'event_type', 'is_all_day')
    list_filter = ('event_type', 'user', 'is_all_day')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_date'
    ordering = ('-start_date',)