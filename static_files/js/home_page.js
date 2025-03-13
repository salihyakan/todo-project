// Event Listener for CTA Button
document.querySelector('.cta-button').addEventListener('click', function () {
    window.location.href = '/kayit-ol'; // Redirect to registration page
});

// Card Data
const cards = {
    1: {
        title: "Hızlı Başlangıç",
        content: "Sade 3 adımda hedeflerini belirle ve takibe başla!",
        icon: "rocket",
        color: "#ff8b94"
    },
    2: {
        title: "Takım Yönetimi",
        content: "Görevlerini yönet, not al ve hatırlatıcılarını ayarla",
        icon: "users",
        color: "#a8e6cf"
    },
    3: {
        title: "Detaylı İstatistikler",
        content: "Aylık performansını takip et, hedeflerini analiz et",
        icon: "chart-line",
        color: "#ffd3b6"
    },
    4: {
        title: "Sade ve Güvenli",
        content: "Kolay kullanım ve güvenli veri saklama",
        icon: "shield-alt",
        color: "#d4a5a5"
    }
};

// Interactive Card System
document.querySelectorAll('.feature-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        // Update active button
        document.querySelector('.feature-btn.active').classList.remove('active');
        this.classList.add('active');

        // Create cards
        const cardId = this.dataset.card;
        const container = document.querySelector('.cards-container');
        container.innerHTML = `
            <div class="card">
                <h3><i class="fas fa-${cards[cardId].icon}"></i> ${cards[cardId].title}</h3>
                <p>${cards[cardId].content}</p>
            </div>
        `;
    });
});

// Load the first card
document.querySelector('.feature-btn').click();

// Carousel Navigation
const carousel = document.querySelector('.carousel');
const prevBtn = document.querySelector('.prev-btn');
const nextBtn = document.querySelector('.next-btn');
let scrollAmount = 0;

nextBtn.addEventListener('click', () => {
    const cardWidth = document.querySelector('.task-card').offsetWidth + 24;
    carousel.scrollBy({ left: cardWidth, behavior: 'smooth' });
});

prevBtn.addEventListener('click', () => {
    const cardWidth = document.querySelector('.task-card').offsetWidth + 24;
    carousel.scrollBy({ left: -cardWidth, behavior: 'smooth' });
});