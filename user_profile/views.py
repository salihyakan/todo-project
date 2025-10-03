import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from .forms import UserUpdateForm, ProfileUpdateForm, LoginForm, RegistrationForm
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView 
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm 
from .models import Profile, Badge, BadgeType, Notification, UserBadge
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q
from .utils import check_user_badges


def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data.get('username')  # Bu artık email
            password = form.cleaned_data.get('password')
            
            # Email backend'i kullanarak authenticate et
            user = authenticate(
                request, 
                username=username, 
                password=password,
                backend='user_profile.backends.EmailBackend'
            )
            
            if user is not None:
                login(request, user, backend='user_profile.backends.EmailBackend')
                messages.success(request, 'Başarıyla giriş yaptınız!')
                
                # next parametresini kontrol et
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('dashboard:home')
            else:
                messages.error(request, 'Geçersiz e-posta veya şifre.')
        else:
            # Form hatalarını mesaj olarak göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")

    return render(request, 'user_profile/login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard:home')
    
    form = RegistrationForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            
            # Backend belirterek kullanıcıyı authenticate et
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Email backend'i kullanarak authenticate et
            user = authenticate(
                request, 
                username=form.cleaned_data.get('email'),  # Email ile authenticate
                password=password,
                backend='user_profile.backends.EmailBackend'
            )
            
            if user is not None:
                # Backend belirterek login yap
                login(request, user, backend='user_profile.backends.EmailBackend')
                messages.success(request, 'Hesabınız başarıyla oluşturuldu! Hoş geldiniz!')
                return redirect('dashboard:home')
            else:
                # Authenticate başarısız olursa, kullanıcıyı login sayfasına yönlendir
                messages.success(request, 'Hesabınız başarıyla oluşturuldu! Lütfen giriş yapın.')
                return redirect('user_profile:login')
        else:
            # Form hatalarını göster
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    
    return render(request, 'user_profile/register.html', {'form': form})


@login_required
def user_logout(request):
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('dashboard:home')

@login_required
def profile(request):
    # Kullanıcının profilini al - select_related ile optimizasyon
    profile = request.user.profile
    
    # DÜZELTME: user_profile üzerinden filtreleme - select_related ile optimizasyon
    badges = UserBadge.objects.filter(user_profile=profile).select_related('badge', 'badge__badge_type')

    # DÜZELTME: user_profile üzerinden görüldü işaretleme
    UserBadge.objects.filter(
        user_profile=profile, 
        is_seen=False
    ).update(is_seen=True)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=profile
        )
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('user_profile:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
        'badges': badges,
    }
    
    return render(request, 'user_profile/profile.html', context)

@login_required
def profile_view(request):
    """Profil görüntüleme sayfası"""
    # select_related ile optimizasyon
    profile = Profile.objects.select_related('user').get(user=request.user)
    badges = UserBadge.objects.filter(user_profile=profile).select_related('badge', 'badge__badge_type')
    
    context = {
        'profile': profile,
        'badges': badges,
    }
    return render(request, 'user_profile/profile.html', context)

@login_required
def profile_edit(request):
    """Profil düzenleme sayfası"""
    profile = request.user.profile
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profiliniz başarıyla güncellendi!')
            return redirect('user_profile:profile')
        else:
            # Form hatalarını göster
            for field, errors in user_form.errors.items():
                for error in errors:
                    messages.error(request, f"Kullanıcı bilgileri: {error}")
            for field, errors in profile_form.errors.items():
                for error in errors:
                    messages.error(request, f"Profil bilgileri: {error}")
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'user_profile/profile_edit.html', context)

class CustomPasswordChangeView(PasswordChangeView):
    template_name = 'user_profile/password_change.html'
    success_url = reverse_lazy('user_profile:password_change_done')

class CustomPasswordChangeDoneView(PasswordChangeDoneView):
    template_name = 'user_profile/password_change_done.html'

class CustomPasswordResetView(PasswordResetView):
    form_class = PasswordResetForm
    template_name = 'user_profile/password_reset.html'
    email_template_name = 'user_profile/password_reset_email.html'
    subject_template_name = 'user_profile/password_reset_subject.txt'
    success_url = reverse_lazy('user_profile:password_reset_done')  # DÜZELTİLDİ
    
    def form_valid(self, form):
        # Email'in konsola yazdırıldığını kontrol etmek için
        print("Password reset formu geçerli, email gönderiliyor...")
        return super().form_valid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'user_profile/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = SetPasswordForm
    template_name = 'user_profile/password_reset_confirm.html'
    success_url = reverse_lazy('user_profile:password_reset_complete')  # DÜZELTİLDİ

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'user_profile/password_reset_complete.html'

@login_required
def update_pomodoro(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            duration = int(data.get('duration'))
            if 5 <= duration <= 60:
                profile = request.user.profile
                profile.pomodoro_duration = duration
                profile.save()
                return JsonResponse({'success': True})
        except (ValueError, TypeError):
            pass
    return JsonResponse({'success': False}, status=400)


@login_required
def badge_list(request):
    if not request.user.is_authenticated:
        return redirect('user_profile:login')
    
    profile = request.user.profile
    # select_related ve annotate ile optimizasyon
    badge_types = BadgeType.objects.annotate(
        total_badges=Count('badges'),
        earned_count=Count('badges__user_badges', filter=Q(badges__user_badges__user_profile=profile))
    )
    
    # Tüm rozetleri ve kullanıcının kazandıklarını getir - select_related ile optimizasyon
    all_badges = Badge.objects.select_related('badge_type').all()
    earned_badges_ids = UserBadge.objects.filter(
        user_profile=profile
    ).values_list('badge_id', flat=True)
    
    # Kazanılan ve kazanılmayan rozetleri ayır
    earned_badges = []
    unearned_badges = []
    
    for badge in all_badges:
        if badge.id in earned_badges_ids:
            badge.earned = True
            earned_badges.append(badge)
        else:
            badge.earned = False
            unearned_badges.append(badge)
    
    # Rozet türlerine göre grupla
    badge_types_with_badges = []
    for badge_type in badge_types:
        type_badges = {
            'earned': [b for b in earned_badges if b.badge_type_id == badge_type.id],
            'unearned': [b for b in unearned_badges if b.badge_type_id == badge_type.id]
        }
        badge_types_with_badges.append({
            'type': badge_type,
            'badges': type_badges,
            'earned_count': len(type_badges['earned']),
            'total_count': badge_type.total_badges
        })
    
    # İlerleme yüzdesini hesapla
    progress_percentage = len(earned_badges) / all_badges.count() * 100 if all_badges.count() > 0 else 0
    
    context = {
        'badge_types': badge_types_with_badges,
        'earned_badges_count': len(earned_badges),
        'total_badges': all_badges.count(),
        'earned_badges': earned_badges,
        'unearned_badges': unearned_badges,
        'progress_percentage': progress_percentage
    }
    return render(request, 'user_profile/badge_list.html', context)

@login_required
def badge_detail(request, slug):
    # select_related ile optimizasyon
    badge = get_object_or_404(Badge.objects.select_related('badge_type'), slug=slug)
    profile = request.user.profile
    
    # Kullanıcının bu rozeti kazanıp kazanmadığını kontrol et
    earned = UserBadge.objects.filter(
        user_profile=profile,
        badge=badge
    ).exists()
    
    # Bu rozet türündeki diğer rozetler - select_related ile optimizasyon
    similar_badges = Badge.objects.filter(
        badge_type=badge.badge_type
    ).select_related('badge_type').exclude(id=badge.id)[:4]
    
    # Bu rozeti kazanan kullanıcı sayısı
    earned_count = UserBadge.objects.filter(badge=badge).count()
    
    # Kriterleri düzgün formatla
    criteria_list = []
    for key, value in badge.criteria.items():
        criteria_list.append(f"{key.replace('_', ' ').title()}: {value}")
    
    context = {
        'badge': badge,
        'user_has_badge': earned,
        'similar_badges': similar_badges,
        'earned_count': earned_count,
        'criteria_list': criteria_list
    }
    return render(request, 'user_profile/badge_detail.html', context)

@login_required
def notifications_view(request):
    # Get unread notifications - optimizasyon: sadece gerekli alanları seç
    unread_notifications = Notification.objects.filter(
        user=request.user, 
        is_read=False
    ).only('id', 'message', 'notification_type', 'created_at', 'url').order_by('-created_at')
    
    # Get all notifications (last 30 days) - optimizasyon: sadece gerekli alanları seç
    all_notifications = Notification.objects.filter(
        user=request.user,
        created_at__gte=timezone.now()-timedelta(days=30)
    ).only('id', 'message', 'notification_type', 'created_at', 'url', 'is_read').order_by('-created_at')
    
    # Mark badge notifications as seen when page is loaded
    UserBadge.objects.filter(
        user_profile=request.user.profile,
        is_seen=False
    ).update(is_seen=True)
    
    return render(request, 'user_profile/notifications.html', {
        'unread_notifications': unread_notifications,
        'all_notifications': all_notifications
    })

@login_required
def clear_history_notifications(request):
    if request.method == 'POST':
        # Kullanıcının okunmuş bildirimlerini sil
        deleted_count, _ = Notification.objects.filter(
            user=request.user,
            is_read=True
        ).delete()
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success', 
                'deleted_count': deleted_count
            })
        
        messages.success(request, f'{deleted_count} bildirim silindi.')
        return redirect('user_profile:notifications')
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def mark_notification_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('user_profile:notifications')

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    
    return redirect('user_profile:notifications')

@login_required
def check_new_notifications(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        last_notification_id = request.GET.get('last_id', 0)
        
        # Son bildirimden sonra yeni bildirim var mı?
        has_new = Notification.objects.filter(
            user=request.user,
            id__gt=last_notification_id
        ).exists()
        
        unread_count = Notification.objects.filter(
            user=request.user,
            is_read=False
        ).count()
        
        return JsonResponse({
            'has_new': has_new,
            'unread_count': unread_count
        })
    return JsonResponse({'error': 'Geçersiz istek'}, status=400)

@login_required
def force_badge_check(request):
    """Rozet kontrolünü manuel tetikleme (test için)"""
    from .utils import check_user_badges  # Eğer gerekliyse import et
    profile = request.user.profile
    check_user_badges(profile)
    
    messages.success(request, 'Rozet kontrolleri güncellendi!')
    return redirect('user_profile:badge_list')