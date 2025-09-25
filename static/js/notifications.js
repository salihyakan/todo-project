document.addEventListener('DOMContentLoaded', function() {
    // Real-time bildirim kontrolü
    function checkForNewNotifications() {
        const lastNotificationId = document.querySelector('.notification-item')?.dataset.id || 0;
        
        fetch(`/profile/notifications/check-new/?last_id=${lastNotificationId}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.has_new) {
                // Yeni bildirim var, sayfayı yenile
                location.reload();
            } else if (data.unread_count > 0) {
                // Sadece sayıyı güncelle
                const badge = document.getElementById('notification-count');
                if (badge) {
                    badge.textContent = data.unread_count;
                    badge.classList.remove('d-none');
                }
            }
        });
    }

    // Her 60 saniyede bir kontrol et
    setInterval(checkForNewNotifications, 60000);
    
    // Bildirim sesi
    const notificationSound = new Audio('{% static "sounds/notification.mp3" %}');
    
    // Bildirim izleme (WebSocket veya SSE için yer tutucu)
    // Gerçek uygulamada WebSocket/SSE kullanılmalı
});