// Todo uygulaması için JavaScript fonksiyonları
document.addEventListener('DOMContentLoaded', function() {
    // Kategori seçim mantığı
    initializeCategorySelection();
    
    // Tarih seçici için flatpickr (opsiyonel)
    initializeDatePickers();
    
    // Görev durumu güncelleme
    initializeStatusUpdates();
    
    // Not modal işlemleri
    initializeNoteModals();
    
    // Responsive davranışlar
    initializeResponsiveBehaviors();
});

function initializeCategorySelection() {
    const categorySelect = document.getElementById('category-select');
    const newCategoryInput = document.getElementById('new-category-input');
    
    if (categorySelect && newCategoryInput) {
        function updateCategoryFields() {
            const hasCategorySelection = categorySelect.value !== '';
            const hasNewCategory = newCategoryInput.value.trim() !== '';
            
            if (hasCategorySelection) {
                newCategoryInput.disabled = true;
                newCategoryInput.placeholder = 'Mevcut kategori seçildi';
                newCategoryInput.classList.add('bg-light');
            } else if (hasNewCategory) {
                categorySelect.disabled = true;
                categorySelect.parentElement.style.opacity = '0.6';
                categorySelect.classList.add('bg-light');
            } else {
                newCategoryInput.disabled = false;
                categorySelect.disabled = false;
                categorySelect.parentElement.style.opacity = '1';
                newCategoryInput.placeholder = 'Yeni kategori adı';
                newCategoryInput.classList.remove('bg-light');
                categorySelect.classList.remove('bg-light');
            }
        }
        
        categorySelect.addEventListener('change', updateCategoryFields);
        newCategoryInput.addEventListener('input', updateCategoryFields);
        
        // Sayfa yüklendiğinde kontrol et
        updateCategoryFields();
    }
}

function initializeDatePickers() {
    // DateTime picker için flatpickr kullanımı (eğer kütüphane mevcutsa)
    if (typeof flatpickr !== 'undefined') {
        const dateInputs = document.querySelectorAll('input[type="datetime-local"]');
        dateInputs.forEach(input => {
            flatpickr(input, {
                enableTime: true,
                dateFormat: "Y-m-d H:i",
                time_24hr: true,
                locale: "tr",
                minDate: "today"
            });
        });
        
        const dateOnlyInputs = document.querySelectorAll('input[type="date"]');
        dateOnlyInputs.forEach(input => {
            flatpickr(input, {
                dateFormat: "Y-m-d",
                locale: "tr",
                minDate: "today"
            });
        });
    }
}

function initializeStatusUpdates() {
    // Görev durumu güncelleme butonları
    const completeButtons = document.querySelectorAll('form[action*="complete"]');
    completeButtons.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            const button = this.querySelector('button[type="submit"]');
            const originalText = button.innerHTML;
            
            // Loading state
            button.innerHTML = '<span class="loading-spinner"></span> İşleniyor...';
            button.disabled = true;
            
            fetch(this.action, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Başarılı mesajı göster ve sayfayı yenile
                    showNotification('Görev başarıyla tamamlandı!', 'success');
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    throw new Error('İşlem başarısız');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                button.innerHTML = originalText;
                button.disabled = false;
                showNotification('Bir hata oluştu, lütfen tekrar deneyin.', 'error');
            });
        });
    });
}

function initializeNoteModals() {
    // Not modal işlemleri
    const noteModal = document.getElementById('noteModal');
    if (noteModal) {
        noteModal.addEventListener('show.bs.modal', function() {
            // Modal açıldığında mevcut notu yükle
            loadExistingNote();
        });
    }
}

function loadExistingNote() {
    const taskId = window.location.pathname.split('/').filter(Boolean).pop();
    fetch(`/todo/${taskId}/get-note/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.querySelector('#noteModal textarea').value = data.content;
            }
        })
        .catch(error => console.error('Error loading note:', error));
}

function initializeResponsiveBehaviors() {
    // Mobil menü için toggle butonu
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.body.classList.toggle('mobile-menu-open');
        });
    }
    
    // Pencere boyutu değiştiğinde kontrol et
    window.addEventListener('resize', function() {
        adjustLayoutForScreenSize();
    });
    
    adjustLayoutForScreenSize();
}

function adjustLayoutForScreenSize() {
    const screenWidth = window.innerWidth;
    const taskCards = document.querySelectorAll('.task-card');
    
    if (screenWidth < 768) {
        // Mobil görünüm için kartları küçült
        taskCards.forEach(card => {
            card.style.fontSize = '0.9em';
        });
    } else {
        taskCards.forEach(card => {
            card.style.fontSize = '';
        });
    }
}

// Bildirim gösterme fonksiyonu
function showNotification(message, type = 'info') {
    // Basit bir toast bildirim sistemi
    const toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        createToastContainer();
    }
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-bg-${type === 'error' ? 'danger' : type} border-0`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;
    
    document.getElementById('toast-container').appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Toast gösterildikten sonra kaldır
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '9999';
    document.body.appendChild(container);
}

// Form validation helper
function validateForm(form) {
    const inputs = form.querySelectorAll('input[required], select[required], textarea[required]');
    let isValid = true;
    
    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('is-invalid');
            isValid = false;
        } else {
            input.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Tarih formatlama helper'ı
function formatDate(dateString) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(dateString).toLocaleDateString('tr-TR', options);
}

// Kalan süre hesaplama
function calculateTimeRemaining(dueDate) {
    const now = new Date();
    const due = new Date(dueDate);
    const diff = due - now;
    
    if (diff <= 0) {
        return 'Süresi doldu';
    }
    
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    
    if (days > 0) {
        return `${days} gün ${hours} saat`;
    } else if (hours > 0) {
        return `${hours} saat`;
    } else {
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
        return `${minutes} dakika`;
    }
}