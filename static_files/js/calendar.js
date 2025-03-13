document.addEventListener('DOMContentLoaded', () => {
    let currentDate = new Date();
    let selectedDate = null;
    const notes = JSON.parse(localStorage.getItem('calendarNotes')) || {};

    // Generate calendar
    function generateCalendar() {
        const calendarGrid = document.getElementById('calendarGrid');
        calendarGrid.innerHTML = '';

        // Weekday headers
        ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'].forEach(day => {
            calendarGrid.innerHTML += `<div class="calendar-day-label">${day}</div>`;
        });

        const year = currentDate.getFullYear();
        const month = currentDate.getMonth();
        document.getElementById('currentMonth').textContent =
            `${new Date(year, month).toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' })}`;

        const firstDay = (new Date(year, month, 1).getDay() || 7) - 1; // 0=Monday
        const daysInMonth = new Date(year, month + 1, 0).getDate();

        // Adjust empty cells for Monday start
        for (let i = 0; i < firstDay; i++) {
            calendarGrid.innerHTML += `<div class="day-cell other-month"></div>`;
        }

        // Day cells
        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(year, month, day);
            const dateKey = date.toISOString().split('T')[0];
            const isToday = date.toDateString() === new Date().toDateString();

            calendarGrid.innerHTML += `
            <div class="day-cell ${isToday ? 'current-day' : ''}" data-date="${dateKey}">
                <div class="hover-overlay">
                    <span class="hover-text">
                        ${notes[dateKey] ? 'Notu Düzenle' : 'Not Ekle'}
                    </span>
                </div>
                <span class="day-number">${day}</span>
                ${notes[dateKey] ? `
                    <div class="note-preview">
                        <i class="fa-solid fa-note-sticky"></i>
                        <span class="note-text">${notes[dateKey].substring(0, 20)}${notes[dateKey].length > 20 ? '...' : ''}</span>
                    </div>
                ` : ''}
            </div>`;
        }

        // Day click event
        document.querySelectorAll('.day-cell').forEach(cell => {
            cell.addEventListener('click', () => {
                selectedDate = cell.dataset.date;
                openNotesModal(selectedDate);
            });
        });
    }

    // Open modal
    function openNotesModal(date) {
        const modal = document.getElementById('notesModal');
        const dateObj = new Date(date);
        document.getElementById('selectedDateHeader').textContent =
            dateObj.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
        document.getElementById('noteInput').value = notes[date] || '';
        modal.style.display = 'block';
    }

    // Close modal
    function closeNotesModal() {
        document.getElementById('notesModal').style.display = 'none';
    }

    // Add delete button functionality
    document.getElementById('deleteNoteBtn').addEventListener('click', () => {
        if (selectedDate && confirm("Bu notu tamamen silmek istediğinize emin misiniz?")) {
            delete notes[selectedDate];
            localStorage.setItem('calendarNotes', JSON.stringify(notes));
            generateCalendar();
            closeNotesModal();
        }
    });

    // Event listeners
    document.getElementById('prevMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        generateCalendar();
    });

    document.getElementById('nextMonth').addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        generateCalendar();
    });

    document.querySelector('.close-modal').addEventListener('click', closeNotesModal);
    document.querySelector('.save-note-btn').addEventListener('click', () => {
        if (selectedDate) {
            notes[selectedDate] = document.getElementById('noteInput').value;
            localStorage.setItem('calendarNotes', JSON.stringify(notes));
            generateCalendar(); // Refresh note indicator
            closeNotesModal();
        }
    });

    // Close modal on outside click
    window.onclick = function (event) {
        const modal = document.getElementById('notesModal');
        if (event.target === modal) {
            closeNotesModal();
        }
    }

    // Close modal on ESC key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeNotesModal();
    });

    generateCalendar();
});