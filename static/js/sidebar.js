// Global Pomodoro Timer Management
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
        this.timerInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.checkAndStartTimer();
        
        // State değişikliklerini dinle
        this.setupStateListener();
        
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
        // Her saniye state'i kontrol et
        setInterval(() => {
            this.checkAndUpdateState();
        }, 1000);
        
        // Storage değişikliklerini dinle (diğer tablardan gelen değişiklikler için)
        window.addEventListener('storage', (e) => {
            if (e.key === 'pomodoroTimerState') {
                this.checkAndUpdateState();
            }
        });
    }
    
    checkAndUpdateState() {
        const savedState = localStorage.getItem('pomodoroTimerState');
        if (savedState) {
            const stateData = JSON.parse(savedState);
            
            // Eğer timer çalışıyorsa, geçen süreyi hesapla
            if (stateData.isRunning) {
                const timeElapsed = Math.floor((Date.now() - stateData.savedAt) / 1000);
                stateData.timeLeft = Math.max(0, stateData.timeLeft - timeElapsed);
                
                // Eğer süre dolmuşsa
                if (stateData.timeLeft <= 0) {
                    this.handleTimerComplete(stateData);
                } else {
                    // Timer çalışıyorsa ama bizim intervalimiz yoksa başlat
                    if (!this.timerInterval) {
                        this.startLocalTimer(stateData);
                    }
                }
            } else {
                // Timer çalışmıyorsa interval'i temizle
                if (this.timerInterval) {
                    clearInterval(this.timerInterval);
                    this.timerInterval = null;
                }
            }
            
            this.updateDisplay(stateData);
        }
    }
    
    checkAndStartTimer() {
        const savedState = localStorage.getItem('pomodoroTimerState');
        if (savedState) {
            const stateData = JSON.parse(savedState);
            
            if (stateData.isRunning) {
                const timeElapsed = Math.floor((Date.now() - stateData.savedAt) / 1000);
                stateData.timeLeft = Math.max(0, stateData.timeLeft - timeElapsed);
                
                if (stateData.timeLeft <= 0) {
                    this.handleTimerComplete(stateData);
                } else {
                    this.startLocalTimer(stateData);
                }
            }
            
            this.updateDisplay(stateData);
        }
    }
    
    startLocalTimer(stateData) {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }
        
        this.timerInterval = setInterval(() => {
            const currentState = this.getCurrentState();
            if (currentState && currentState.isRunning) {
                currentState.timeLeft--;
                
                if (currentState.timeLeft <= 0) {
                    this.handleTimerComplete(currentState);
                } else {
                    this.saveState(currentState);
                    this.updateDisplay(currentState);
                }
            } else {
                clearInterval(this.timerInterval);
                this.timerInterval = null;
            }
        }, 1000);
    }
    
    getCurrentState() {
        const savedState = localStorage.getItem('pomodoroTimerState');
        return savedState ? JSON.parse(savedState) : null;
    }
    
    saveState(state) {
        const stateToSave = {
            ...state,
            savedAt: Date.now()
        };
        localStorage.setItem('pomodoroTimerState', JSON.stringify(stateToSave));
        
        // Storage event'ini tetikle (diğer tablar için)
        window.dispatchEvent(new StorageEvent('storage', {
            key: 'pomodoroTimerState',
            newValue: JSON.stringify(stateToSave)
        }));
    }
    
    start() {
        const currentState = this.getCurrentState();
        if (!currentState) return;
        
        if (currentState.isRunning) return;
        
        // Eğer pomodoro sayfasındaysak, oradaki timer'ı başlat
        if (window.location.pathname === this.pomodoroUrl) {
            if (window.startTimer) {
                window.startTimer();
                return;
            }
        }
        
        // Değilse kendi timer'ımızı başlat
        currentState.isRunning = true;
        currentState.savedAt = Date.now();
        this.saveState(currentState);
        this.startLocalTimer(currentState);
    }
    
    pause() {
        const currentState = this.getCurrentState();
        if (!currentState) return;
        
        if (!currentState.isRunning) return;
        
        if (window.location.pathname === this.pomodoroUrl && window.pauseTimer) {
            window.pauseTimer();
        } else {
            this.pauseTimer();
        }
    }
    
    pauseTimer() {
        const currentState = this.getCurrentState();
        if (!currentState) return;
        
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        currentState.isRunning = false;
        this.saveState(currentState);
        this.updateDisplay(currentState);
    }
    
    reset() {
        if (window.location.pathname === this.pomodoroUrl && window.resetTimer) {
            window.resetTimer();
        } else {
            this.resetTimer();
        }
    }
    
    resetTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        const resetState = {
            workTime: 25 * 60,
            breakTime: 5 * 60,
            timeLeft: 25 * 60,
            isRunning: false,
            isWorkPhase: true,
            completedSessions: 0,
            totalSessions: 4,
            currentSession: 1,
            savedAt: Date.now()
        };
        
        this.saveState(resetState);
        this.updateDisplay(resetState);
    }
    
    handleTimerComplete(stateData) {
        // Interval'i temizle
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        stateData.isRunning = false;
        
        if (stateData.isWorkPhase) {
            // Çalışma tamamlandı, mola başlasın
            stateData.isWorkPhase = false;
            stateData.timeLeft = stateData.breakTime;
        } else {
            // Mola tamamlandı, yeni çalışma başlasın
            stateData.isWorkPhase = true;
            stateData.timeLeft = stateData.workTime;
            stateData.completedSessions++;
            stateData.currentSession++;
            
            if (stateData.completedSessions >= stateData.totalSessions) {
                stateData.completedSessions = 0;
                stateData.currentSession = 1;
            }
        }
        
        this.saveState(stateData);
        this.updateDisplay(stateData);
        
        // Otomatik devam et
        setTimeout(() => {
            stateData.isRunning = true;
            stateData.savedAt = Date.now();
            this.saveState(stateData);
            this.startLocalTimer(stateData);
        }, 2000);
    }
    
    updateDisplay(stateData) {
        if (!stateData) return;
        
        if (this.timerElement) {
            this.timerElement.textContent = this.formatTime(stateData.timeLeft);
        }
        if (this.phaseElement) {
            this.phaseElement.textContent = stateData.isWorkPhase ? 'Çalışma' : 'Mola';
        }
        
        // Mini elementin class'ını güncelle (renk için)
        if (this.miniElement) {
            this.miniElement.classList.remove('work-phase', 'break-phase');
            this.miniElement.classList.add(stateData.isWorkPhase ? 'work-phase' : 'break-phase');
        }
    }
    
    formatTime(seconds) {
        const mins = Math.floor(seconds / 60).toString().padStart(2, '0');
        const secs = (seconds % 60).toString().padStart(2, '0');
        return `${mins}:${secs}`;
    }
    
    close() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
        
        this.miniElement.style.display = 'none';
        localStorage.setItem('pomodoroMiniClosed', 'true');
    }
}

// Sayfa yüklendiğinde mini pomodoro'yu başlat
document.addEventListener('DOMContentLoaded', function() {
    // Eğer kullanıcı daha önce kapatmadıysa veya timer çalışıyorsa göster
    const isClosed = localStorage.getItem('pomodoroMiniClosed');
    const timerState = localStorage.getItem('pomodoroTimerState');
    
    let shouldShow = true;
    
    if (isClosed === 'true') {
        const state = timerState ? JSON.parse(timerState) : null;
        shouldShow = state && state.isRunning; // Timer çalışıyorsa göster
    }
    
    if (shouldShow) {
        window.pomodoroMini = new PomodoroMini();
    }
    
    // Bildirim izni iste
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
});