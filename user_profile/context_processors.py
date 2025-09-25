from .models import Notification, UserBadge

def badge_notifications(request):
    if request.user.is_authenticated:
        new_badges_count = UserBadge.objects.filter(
            user_profile=request.user.profile, 
            is_seen=False
        ).count()
        return {'new_badges_count': new_badges_count}
    return {'new_badges_count': 0}

def notifications(request):
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            user=request.user, 
            is_read=False
        ).count()
        
        recent_notifications = Notification.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        
        return {
            'unread_notifications_count': unread_count,
            'recent_notifications': recent_notifications
        }
    return {}