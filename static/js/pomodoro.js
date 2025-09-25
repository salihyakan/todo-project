document.addEventListener('DOMContentLoaded', function() {
    const timerDisplay = document.getElementById('timer');
    const startBtn = document.getElementById('startBtn');
    const pauseBtn = document.getElementById('pauseBtn');
    const resetBtn = document.getElementById('resetBtn');
    const durationInput = document.getElementById('pomodoroDuration');
    const saveSettingsBtn = document.getElementById('saveSettings');
    const durationButtons = document.querySelectorAll('[data-minutes]');
    
    let countdown;
    let minutes = parseInt(durationInput.value);
    let seconds = 0;
    let isRunning = false;
    
    // Süreyi güncelle
    function updateDisplay() {
        timerDisplay.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }
    
    // Süre seçme butonları
    durationButtons.forEach(button => {
        button.addEventListener('click', function() {
            minutes = parseInt(this.dataset.minutes);
            seconds = 0;
            durationInput.value = minutes;
            updateDisplay();
        });
    });
    
    // Zamanlayıcıyı başlat
    function startTimer() {
        if (isRunning) return;
        
        isRunning = true;
        startBtn.disabled = true;
        pauseBtn.disabled = false;
        
        countdown = setInterval(() => {
            if (seconds === 0) {
                if (minutes === 0) {
                    clearInterval(countdown);
                    playAlarm();
                    isRunning = false;
                    startBtn.disabled = false;
                    pauseBtn.disabled = true;
                    return;
                }
                minutes--;
                seconds = 59;
            } else {
                seconds--;
            }
            
            updateDisplay();
        }, 1000);
    }
    
    // Zamanlayıcıyı duraklat
    function pauseTimer() {
        clearInterval(countdown);
        isRunning = false;
        startBtn.disabled = false;
        pauseBtn.disabled = true;
    }
    
    // Zamanlayıcıyı sıfırla
    function resetTimer() {
        clearInterval(countdown);
        isRunning = false;
        minutes = parseInt(durationInput.value);
        seconds = 0;
        updateDisplay();
        startBtn.disabled = false;
        pauseBtn.disabled = true;
    }
    
    // Alarm sesi çal
    function playAlarm() {
        const audio = new Audio('{% static "sounds/alarm.mp3" %}');
        audio.play();
        alert('Pomodoro süreniz tamamlandı!');
    }
    
    // Ayarları kaydet
    function saveSettings() {
        const newDuration = parseInt(durationInput.value);
        if (newDuration > 0 && newDuration <= 60) {
            minutes = newDuration;
            resetTimer();
            
            // Sunucuya kaydetme (AJAX ile)
            fetch('/profile/update_pomodoro/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ duration: newDuration })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Ayarlar kaydedildi!');
                }
            });
        }
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
    
    // Olay dinleyicileri
    startBtn.addEventListener('click', startTimer);
    pauseBtn.addEventListener('click', pauseTimer);
    resetBtn.addEventListener('click', resetTimer);
    saveSettingsBtn.addEventListener('click', saveSettings);
    
    // Başlangıçta süreyi güncelle
    updateDisplay();
});