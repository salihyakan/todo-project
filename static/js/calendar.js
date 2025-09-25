
document.addEventListener('DOMContentLoaded', function () {

    // CSRF Token fonksiyonu
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

    // Takvimi başlat
    const calendarEl = document.getElementById('calendar');
    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'tr',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },
        firstDay: 1, // Pazartesi
        editable: true,
        dayMaxEvents: true,
        events: {
            url: "{% url 'dashboard:calendar_events' %}",
            method: 'GET',
            failure: function() {
                alert('Etkinlikler yüklenirken hata oluştu!');
            }
        },
        eventClick: function (info) {
            const eventModal = new bootstrap.Modal(document.getElementById('eventModal'));
            const start = info.event.start ? info.event.start.toLocaleString('tr-TR') : 'Belirtilmemiş';
            const end = info.event.end ? info.event.end.toLocaleString('tr-TR') : 'Belirtilmemiş';
            const eventType = info.event.extendedProps.type;

            document.getElementById('eventModalTitle').textContent = info.event.title;
            document.getElementById('eventModalType').textContent = getEventTypeName(eventType);
            document.getElementById('eventModalStart').textContent = start;
            document.getElementById('eventModalEnd').textContent = end;
            document.getElementById('eventModalDesc').textContent = info.event.extendedProps.description || 'Açıklama yok';

            // Sil ve Düzenle butonlarına event id'sini ekle
            document.getElementById('deleteEventBtn').dataset.eventId = info.event.id;
            document.getElementById('editEventBtn').dataset.eventId = info.event.id;

            eventModal.show();
        },
        dateClick: function (info) {
            const newEventModal = new bootstrap.Modal(document.getElementById('newEventModal'));

            // Tarih formatını ayarla (YYYY-MM-DDTHH:mm)
            const formattedDate = info.dateStr + 'T00:00';
            document.querySelector('#newEventForm input[name="start_date"]').value = formattedDate;

            newEventModal.show();
        },
        eventClassNames: function (arg) {
            return ['fc-event-' + arg.event.extendedProps.type];
        }
    });

    calendar.render();

    // View değiştirme butonları
    document.getElementById('monthView')?.addEventListener('click', function() {
        calendar.changeView('dayGridMonth');
        setActiveButton(this);
    });

    document.getElementById('weekView').addEventListener('click', function () {
        calendar.changeView('timeGridWeek');
        setActiveButton(this);
    });

    document.getElementById('dayView').addEventListener('click', function () {
        calendar.changeView('timeGridDay');
        setActiveButton(this);
    });

    // Bugün butonu
    document.getElementById('todayBtn').addEventListener('click', function () {
        calendar.today();
    });

    // Yeni etkinlik formu
    document.getElementById('newEventForm').addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = {
            title: this.querySelector('[name="title"]').value,
            start_date: this.querySelector('[name="start_date"]').value,
            end_date: this.querySelector('[name="end_date"]').value || null,
            event_type: this.querySelector('[name="event_type"]').value,
            description: this.querySelector('[name="description"]').value,
            all_day: this.querySelector('[name="all_day"]').checked
        };

        fetch("{% url 'dashboard:create_calendar_event' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(formData)
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    calendar.refetchEvents();
                    bootstrap.Modal.getInstance(document.getElementById('newEventModal')).hide();
                    this.reset();
                } else {
                    alert('Hata: ' + data.message);
                }
            })
            .catch(error => {
                alert('Bir hata oluştu: ' + error);
            });
    });

    // Yardımcı fonksiyonlar
    function setActiveButton(activeBtn) {
        document.querySelectorAll('#monthView, #weekView, #dayView').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
    }

    function getEventTypeName(type) {
        const types = {
            'task': 'Görev',
            'note': 'Not',
            'reminder': 'Hatırlatıcı',
            'event': 'Etkinlik'
        };
        return types[type] || type;
    }
});