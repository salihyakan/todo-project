// Görev durumunu güncelleme
document.addEventListener('DOMContentLoaded', function() {
    // Durum güncelleme butonları
    const statusButtons = document.querySelectorAll('.status-btn');
    
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const taskId = this.dataset.taskId;
            const status = this.dataset.status;
            
            updateTaskStatus(taskId, status);
        });
    });
    
    // Görev durumunu AJAX ile güncelleme
    function updateTaskStatus(taskId, status) {
        fetch(`/todo/${taskId}/update-status/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify({ status: status })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Sayfayı yenile
                location.reload();
            }
        })
        .catch(error => console.error('Error:', error));
    }
    
    // CSRF token almak için yardımcı fonksiyon
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});