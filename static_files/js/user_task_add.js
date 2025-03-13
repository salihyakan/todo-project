document.addEventListener('DOMContentLoaded', function () {
  const taskInputField = document.getElementById('taskInputField');
  const subPanel = document.getElementById('subPanel');
  const saveBtn = document.querySelector('.save-btn');

  let isPanelOpen = false;

  // Open panel on input click
  taskInputField.addEventListener('click', function () {
    subPanel.style.display = 'flex';
    isPanelOpen = true;
  });

  // Listen for clicks on the document
  document.addEventListener('click', function (e) {
    // Check if the clicked element is inside the panel
    const isClickInsidePanel = subPanel.contains(e.target);
    const isClickOnInput = taskInputField.contains(e.target);

    if (!isClickInsidePanel && !isClickOnInput && isPanelOpen) {
      subPanel.style.display = 'none';
      isPanelOpen = false;
    }
  });

  // New JavaScript Additions
  // Calendar Operations
  const dateButton = document.getElementById('dateButton');
  const taskDateInput = document.getElementById('taskDate');

  // Adjust the date input to the button size
  taskDateInput.style.height = dateButton.offsetHeight + 'px';
  taskDateInput.style.width = dateButton.offsetWidth + 'px';

  taskDateInput.addEventListener('change', (e) => {
    const selectedDate = new Date(e.target.value);
    const formattedDate = selectedDate.toLocaleDateString('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
    dateButton.querySelector('span').textContent = formattedDate;
  });

  // Forward clicks on the button to the input
  dateButton.addEventListener('click', (e) => {
    taskDateInput.showPicker(); // For mobile compatibility
  });

  // Category Selection
  const categoryButton = document.getElementById('categoryButton');
  const categoryDropdown = document.getElementById('categoryDropdown');

  categoryButton.addEventListener('click', (e) => {
    e.stopPropagation();
    categoryDropdown.style.display = 'block';
  });

  document.querySelectorAll('.category-item').forEach(item => {
    item.addEventListener('click', () => {
      categoryButton.querySelector('span').textContent = item.textContent;
      categoryDropdown.style.display = 'none';
    });
  });

  // Priority Selection
  const priorityButton = document.getElementById('priorityButton');
  const priorityDropdown = document.getElementById('priorityDropdown');

  priorityButton.addEventListener('click', (e) => {
    e.stopPropagation();
    priorityDropdown.style.display = 'block';
  });

  document.querySelectorAll('.priority-item').forEach(item => {
    item.addEventListener('click', () => {
      priorityButton.querySelector('span').textContent = item.textContent;
      priorityDropdown.style.display = 'none';
      // Update priority color
      priorityButton.style.color = getComputedStyle(item).color;
    });
  });

  // Close dropdowns on outside click
  document.addEventListener('click', (e) => {
    if (!e.target.closest('.dropdown-container')) {
      categoryDropdown.style.display = 'none';
      priorityDropdown.style.display = 'none';
    }
  });

  // Separate event listener for save button
  saveBtn.addEventListener('click', function () {
    subPanel.style.display = 'none';
    taskInputField.value = '';
    isPanelOpen = false;
    // Save operations...
    console.log('Task saved!');
  });

  // Auto resize for textarea
  const textarea = document.querySelector('.task-description');
  const charCounter = document.querySelector('.char-counter');

  textarea.addEventListener('input', (e) => {
    const currentLength = e.target.value.length;
    charCounter.textContent = `${currentLength}/500`;

    // Color change
    if (currentLength > 450) {
      charCounter.style.color = '#ff6b6b';
    } else if (currentLength > 300) {
      charCounter.style.color = '#ffd3b6';
    } else {
      charCounter.style.color = '#94a3b8';
    }
  });

  // Auto resize function
  function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
  }

  textarea.addEventListener('input', () => autoResize(textarea));
  autoResize(textarea); // Initial resize on load
});

