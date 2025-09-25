from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, BadgeType, Badge, UserBadge, Notification

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_select_related = ('profile',)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location', 'pomodoro_duration', 'daily_goal')
    search_fields = ('user__username', 'location')
    list_filter = ('pomodoro_duration', 'daily_goal')

@admin.register(BadgeType)
class BadgeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color')
    search_fields = ('name', 'description')
    list_editable = ('color',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'is_secret', 'slug')
    list_filter = ('badge_type', 'is_secret')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'badge', 'awarded_at', 'is_seen')
    list_filter = ('badge', 'user_profile__user', 'is_seen')
    date_hierarchy = 'awarded_at'
    list_editable = ('is_seen',)
    
    def get_user(self, obj):
        return obj.user_profile.user.username
    get_user.short_description = 'Kullanıcı'