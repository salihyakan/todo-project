class PomodoroManager {
    constructor() {
        this.listeners = [];
        this.currentState = null;
        this.init();
    }

    init() {
        // Mevcut state'i yükle
        this.loadState();
        
        // Storage değişikliklerini dinle
        window.addEventListener('storage', (e) => {
            if (e.key === 'pomodoroTimerState') {
                this.loadState();
                this.notifyListeners();
            }
        });

        // Periyodik state kontrolü
        setInterval(() => {
            this.checkState();
        }, 1000);

        console.log('Pomodoro Manager başlatıldı');
    }

    loadState() {
        const savedState = localStorage.getItem('pomodoroTimerState');
        if (savedState) {
            try {
                this.currentState = JSON.parse(savedState);
                
                // Eğer timer çalışıyorsa, geçen süreyi hesapla
                if (this.currentState.isRunning) {
                    const timeElapsed = Math.floor((Date.now() - this.currentState.savedAt) / 1000);
                    this.currentState.timeLeft = Math.max(0, this.currentState.timeLeft - timeElapsed);
                    this.currentState.savedAt = Date.now();
                    
                    if (this.currentState.timeLeft <= 0) {
                        this.handleTimerComplete();
                    } else {
                        this.saveState();
                    }
                }
            } catch (error) {
                console.error('State yükleme hatası:', error);
                this.createDefaultState();
            }
        } else {
            this.createDefaultState();
        }
    }

    createDefaultState() {
        this.currentState = {
            workTime: 25 * 60,
            breakTime: 5 * 60,
            timeLeft: 25 * 60,
            isRunning: false,
            isWorkPhase: true,
            completedSessions: 0,
            totalSessions: 4,
            currentSession: 1,
            savedAt: Date.now(),
            motivationMessage: this.getRandomMotivationMessage(true),
            // Motivasyon mesajının değişim zamanını kaydet
            motivationLastUpdated: Date.now()
        };
        this.saveState();
    }

    saveState() {
        if (this.currentState) {
            const stateToSave = {
                ...this.currentState,
                savedAt: Date.now()
            };
            localStorage.setItem('pomodoroTimerState', JSON.stringify(stateToSave));
            
            // Storage event'ini tetikle
            window.dispatchEvent(new StorageEvent('storage', {
                key: 'pomodoroTimerState',
                newValue: JSON.stringify(stateToSave)
            }));
            
            this.notifyListeners();
        }
    }

    addListener(callback) {
        this.listeners.push(callback);
        // Mevcut state'i hemen bildir
        if (this.currentState) {
            setTimeout(() => callback(this.currentState), 0);
        }
    }

    removeListener(callback) {
        this.listeners = this.listeners.filter(listener => listener !== callback);
    }

    notifyListeners() {
        this.listeners.forEach((listener) => {
            try {
                listener(this.currentState);
            } catch (error) {
                console.error('Listener hatası:', error);
            }
        });
    }

    checkState() {
        if (this.currentState && this.currentState.isRunning) {
            const timeElapsed = Math.floor((Date.now() - this.currentState.savedAt) / 1000);
            if (timeElapsed > 0) {
                this.currentState.timeLeft = Math.max(0, this.currentState.timeLeft - timeElapsed);
                this.currentState.savedAt = Date.now();
                
                if (this.currentState.timeLeft <= 0) {
                    this.handleTimerComplete();
                } else {
                    this.saveState();
                }
            }
        }
    }

    start() {
        if (this.currentState && !this.currentState.isRunning) {
            this.currentState.isRunning = true;
            this.currentState.savedAt = Date.now();
            this.saveState();
        }
    }

    pause() {
        if (this.currentState && this.currentState.isRunning) {
            this.currentState.isRunning = false;
            this.saveState();
        }
    }

    reset() {
        if (this.currentState) {
            this.currentState = {
                workTime: this.currentState.workTime,
                breakTime: this.currentState.breakTime,
                timeLeft: this.currentState.isWorkPhase ? this.currentState.workTime : this.currentState.breakTime,
                isRunning: false,
                isWorkPhase: true,
                completedSessions: 0,
                totalSessions: this.currentState.totalSessions,
                currentSession: 1,
                savedAt: Date.now(),
                motivationMessage: this.getRandomMotivationMessage(true),
                motivationLastUpdated: Date.now()
            };
            this.saveState();
        }
    }

    handleTimerComplete() {
        if (!this.currentState) return;
        
        this.currentState.isRunning = false;
        
        if (this.currentState.isWorkPhase) {
            // Çalışma tamamlandı, mola başlasın
            this.currentState.isWorkPhase = false;
            this.currentState.timeLeft = this.currentState.breakTime;
            this.currentState.motivationMessage = this.getRandomMotivationMessage(false);
            this.currentState.motivationLastUpdated = Date.now();
        } else {
            // Mola tamamlandı, yeni çalışma başlasın
            this.currentState.isWorkPhase = true;
            this.currentState.timeLeft = this.currentState.workTime;
            this.currentState.completedSessions++;
            this.currentState.currentSession++;
            this.currentState.motivationMessage = this.getRandomMotivationMessage(true);
            this.currentState.motivationLastUpdated = Date.now();
            
            if (this.currentState.completedSessions >= this.currentState.totalSessions) {
                this.currentState.completedSessions = 0;
                this.currentState.currentSession = 1;
            }
        }
        
        this.saveState();
        
        // Otomatik devam et
        setTimeout(() => {
            if (this.currentState) {
                this.currentState.isRunning = true;
                this.currentState.savedAt = Date.now();
                this.saveState();
            }
        }, 2000);
    }

    getRandomMotivationMessage(isWorkPhase) {
        // Genişletilmiş motivasyon sözleri (50+ adet)
        const workMessages = [
            "Konsantrasyon, başarının anahtarıdır. Şimdi odaklanma zamanı!",
            "Her dakika değerli, iyi kullan!",
            "Hedeflerine bir adım daha yaklaşıyorsun.",
            "Mükemmel iş çıkarıyorsun, devam et!",
            "Zorluklar seni daha güçlü yapar. Pes etme!",
            "Başarı, küçük çabaların tekrarlanmasıdır.",
            "Bugünün işini yarına bırakma!",
            "Odaklan, başaracaksın!",
            "Her görev, seni hedefine biraz daha yaklaştırır.",
            "Disiplin, özgürlüğün anahtarıdır.",
            "Şimdi çalış, sonra rahatla.",
            "Zamanın efendisi ol, kölesi değil!",
            "Bu çalışma, senin geleceğini şekillendiriyor.",
            "Kendine inan, yapabilirsin!",
            "Küçük başlangıçlar, büyük bitişler getirir.",
            "Azim, başarının temelidir.",
            "Her şey seninle başlar, seninle biter.",
            "Bugün yapacağın çalışma, yarınki başarının temelidir.",
            "Hayallerine giden yolda bir adım daha at!",
            "Çalışmak, başarının anahtarıdır.",
            "Zor işler, seni güçlendirir.",
            "Her zorluk bir fırsattır.",
            "İlerleme, küçük adımlarla gelir.",
            "Mükemmellik bir alışkanlıktır, tesadüf değil.",
            "Bugün zorlanıyorsan, yarın daha güçlü olacaksın.",
            "Hedeflerin, seni motive etsin!",
            "Çalışma azmin takdir edilesi!",
            "Zihnini odakla, gerisi gelecektir.",
            "Her başarı hikayesi bir gün başladı.",
            "Sen de başarabilirsin, yeter ki inan!"
        ];

        const breakMessages = [
            "Mola zamanı! Zihnini dinlendir.",
            "Gözlerini dinlendirmeyi unutma.",
            "Kısa bir mola, daha iyi odaklanmana yardımcı olur.",
            "Ayağa kalk ve biraz hareket et.",
            "Derin bir nefes al ve rahatla.",
            "Mola, daha iyi odaklanmanı sağlar.",
            "Zihnini boşalt, yeniden odaklan.",
            "Bir şeyler atıştır ve enerji topla.",
            "Gözlerini kapat ve biraz dinlen.",
            "Mola, üretkenliğin bir parçasıdır.",
            "Biraz esneme hareketleri yap.",
            "Su içmeyi unutma!",
            "Mola ver, zihnini tazele.",
            "Kısa bir mola, uzun vadeli verimlilik getirir.",
            "Dinlenmek, daha iyi performans demektir.",
            "Mola, yeni bir başlangıçtır.",
            "Zihnini topla, mola bitince devam et.",
            "Biraz müzik dinle ve rahatla.",
            "Gözlerini uzağa odakla ve dinlendir.",
            "Mola, kendine yapacağın bir iyiliktir.",
            "Dinlenmek de bir üretkenliktir.",
            "Bedenini dinle, ihtiyaçlarını karşıla.",
            "Mola, yaratıcılığını artırır.",
            "Kısa bir yürüyüş yap, enerjin artsın.",
            "Gözlerini kapatarak 1 dakika dinlen.",
            "Derin nefes al, stresini azalt.",
            "Mola, düşüncelerini organize etme zamanı.",
            "Kendine zaman ayır, bu senin hakkın.",
            "Dinlenmiş bir zihin daha iyi çalışır.",
            "Mola bitince daha enerjik döneceksin!"
        ];

        const messages = isWorkPhase ? workMessages : breakMessages;
        const randomIndex = Math.floor(Math.random() * messages.length);
        return messages[randomIndex];
    }

    updateSettings(settings) {
        this.currentState.workTime = settings.workTime * 60;
        this.currentState.breakTime = settings.breakTime * 60;
        this.currentState.totalSessions = settings.totalSessions;
        
        if (!this.currentState.isRunning) {
            this.currentState.timeLeft = this.currentState.isWorkPhase ? 
                this.currentState.workTime : this.currentState.breakTime;
        }
        
        this.saveState();
    }

    // Motivasyon mesajını yenile (manuel olarak çağrılabilir)
    refreshMotivationMessage() {
        if (this.currentState) {
            this.currentState.motivationMessage = this.getRandomMotivationMessage(this.currentState.isWorkPhase);
            this.currentState.motivationLastUpdated = Date.now();
            this.saveState();
        }
    }
}

// Global manager instance'ı oluştur
window.pomodoroManager = new PomodoroManager();