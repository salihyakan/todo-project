class PomodoroMini {
    constructor() {
        this.miniElement = document.getElementById('pomodoro-mini');
        this.timerElement = document.getElementById('mini-timer');
        this.phaseElement = document.getElementById('mini-phase');
        this.startBtn = document.getElementById('mini-start');
        this.pauseBtn = document.getElementById('mini-pause');
        this.resetBtn = document.getElementById('mini-reset');
        this.closeBtn = document.getElementById('mini-close');
        
        this.pomodoroUrl = '/pomodoro/';
        this.stateListener = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.setupStateListener();
        
        // Mini bar'ı göster
        this.showMiniBar();
        
        console.log('Mini Pomodoro başlatıldı');
    }
    
    setupEventListeners() {
        this.startBtn?.addEventListener('click', () => this.start());
        this.pauseBtn?.addEventListener('click', () => this.pause());
        this.resetBtn?.addEventListener('click', () => this.reset());
        this.closeBtn?.addEventListener('click', () => this.close());
        
        this.timerElement?.addEventListener('click', () => {
            window.location.href = this.pomodoroUrl;
        });
    }
    
    setupStateListener() {
        this.stateListener = (state) => {
            this.updateDisplay(state);
        };
        
        window.pomodoroManager.addListener(this.stateListener);
    }
    
    start() {
        window.pomodoroManager.start();
    }
    
    pause() {
        window.pomodoroManager.pause();
    }
    
    reset() {
        window.pomodoroManager.reset();
    }
    
    updateDisplay(state) {
        if (!state) return;
        
        if (this.timerElement) {
            this.timerElement.textContent = this.formatTime(state.timeLeft);
        }
        if (this.phaseElement) {
            this.phaseElement.textContent = state.isWorkPhase ? 'Çalışma' : 'Mola';
        }
        
        // Mini elementin class'ını güncelle (renk için)
        if (this.miniElement) {
            this.miniElement.classList.remove('work-phase', 'break-phase');
            this.miniElement.classList.add(state.isWorkPhase ? 'work-phase' : 'break-phase');
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${mins}:${secs}`;
    }
    
    showMiniBar() {
        const isClosed = localStorage.getItem('pomodoroMiniClosed');
        const timerState = localStorage.getItem('pomodoroTimerState');
        
        let shouldShow = true;
        
        if (isClosed === 'true') {
            const state = timerState ? JSON.parse(timerState) : null;
            shouldShow = state && state.isRunning; // Timer çalışıyorsa göster
        }
        
        if (shouldShow && this.miniElement) {
            this.miniElement.style.display = 'block';
        }
    }
    
    close() {
        if (this.miniElement) {
            this.miniElement.style.display = 'none';
        }
        localStorage.setItem('pomodoroMiniClosed', 'true');
        
        // Listener'ı temizle
        if (this.stateListener) {
            window.pomodoroManager.removeListener(this.stateListener);
        }
    }
}

// Sayfa yüklendiğinde mini pomodoro'yu başlat
document.addEventListener('DOMContentLoaded', function() {
    // Pomodoro manager yüklendiyse mini bar'ı başlat
    if (window.pomodoroManager) {
        window.pomodoroMini = new PomodoroMini();
    }
    
    // Bildirim izni iste
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});