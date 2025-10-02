from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile, BadgeType, Badge, UserBadge, Notification
from .utils import check_user_badges

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
    list_display = ('user', 'location', 'pomodoro_duration', 'daily_goal', 'get_badge_count')
    search_fields = ('user__username', 'location')
    list_filter = ('pomodoro_duration', 'daily_goal')
    actions = ['check_badges_action']
    
    def get_badge_count(self, obj):
        return obj.user_badges.count()
    get_badge_count.short_description = 'Rozet Sayısı'
    
    @admin.action(description='Seçili profiller için rozet kontrolü yap')
    def check_badges_action(self, request, queryset):
        for profile in queryset:
            check_user_badges(profile)
        self.message_user(request, f"{queryset.count()} profil için rozet kontrolü yapıldı.")

@admin.register(BadgeType)
class BadgeTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'color', 'get_badge_count')
    search_fields = ('name', 'description')
    list_editable = ('color',)
    
    def get_badge_count(self, obj):
        return obj.badges.count()
    get_badge_count.short_description = 'Rozet Sayısı'

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'badge_type', 'is_secret', 'slug', 'get_earned_count')
    list_filter = ('badge_type', 'is_secret')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('get_earned_count_display',)
    
    def get_earned_count(self, obj):
        return obj.user_badges.count()
    get_earned_count.short_description = 'Kazanan Sayısı'
    
    def get_earned_count_display(self, obj):
        return f"{obj.user_badges.count()} kullanıcı bu rozeti kazandı"
    get_earned_count_display.short_description = 'Kazanma İstatistiği'

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('get_user', 'badge', 'awarded_at', 'is_seen')
    list_filter = ('badge', 'user_profile__user', 'is_seen')
    date_hierarchy = 'awarded_at'
    list_editable = ('is_seen',)
    actions = ['mark_as_seen_action', 'mark_as_unseen_action']
    
    def get_user(self, obj):
        return obj.user_profile.user.username
    get_user.short_description = 'Kullanıcı'
    
    @admin.action(description='Seçili rozetleri görüldü olarak işaretle')
    def mark_as_seen_action(self, request, queryset):
        updated = queryset.update(is_seen=True)
        self.message_user(request, f"{updated} rozet görüldü olarak işaretlendi.")
    
    @admin.action(description='Seçili rozetleri görülmemiş olarak işaretle')
    def mark_as_unseen_action(self, request, queryset):
        updated = queryset.update(is_seen=False)
        self.message_user(request, f"{updated} rozet görülmemiş olarak işaretlendi.")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
    actions = ['mark_as_read_action', 'mark_as_unread_action']
    
    @admin.action(description='Seçili bildirimleri okundu olarak işaretle')
    def mark_as_read_action(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} bildirim okundu olarak işaretlendi.")
    
    @admin.action(description='Seçili bildirimleri okunmamış olarak işaretle')
    def mark_as_unread_action(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} bildirim okunmamış olarak işaretlendi.")