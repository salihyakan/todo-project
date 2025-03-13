 // Modal Controls
 const editModal = document.getElementById('edit-task-modal');
 const closeBtn = document.querySelector('.close-modal');
 let currentTaskCard = null;
 
 // Open Modal
 function openEditModal(taskCard) {
   currentTaskCard = taskCard;
   
   // Load current values
   document.getElementById('edit-task-name').value = taskCard.querySelector('.task-name').textContent;
   document.getElementById('edit-task-desc').value = taskCard.querySelector('.task-desc').textContent;
   document.getElementById('edit-task-date').value = taskCard.dataset.dueDate;
   
   // Set priority buttons
   const priority = taskCard.dataset.priority;
   document.querySelectorAll('.priority-btn').forEach(btn => {
     btn.classList.remove('active');
     if(btn.dataset.priority === priority) btn.classList.add('active');
   });
   
   // Set category selection
   document.getElementById('edit-task-category').value = taskCard.dataset.category;
   
   editModal.style.display = 'block';
 }
 
 // Close Modal
 function closeEditModal() {
   editModal.style.display = 'none';
   currentTaskCard = null;
 }
 
 // Priority Buttons
 document.querySelectorAll('.priority-btn').forEach(btn => {
   btn.addEventListener('click', function() {
     document.querySelectorAll('.priority-btn').forEach(b => b.classList.remove('active'));
     this.classList.add('active');
   });
 });
 
 // Form Submit
 document.getElementById('edit-task-form').addEventListener('submit', e => {
   e.preventDefault();
   
   if(currentTaskCard) {
     // Update values
     currentTaskCard.querySelector('.task-name').textContent = document.getElementById('edit-task-name').value;
     currentTaskCard.querySelector('.task-desc').textContent = document.getElementById('edit-task-desc').value;
     
     // Priority
     const priority = document.querySelector('.priority-btn.active').dataset.priority;
     currentTaskCard.dataset.priority = priority;
     currentTaskCard.querySelector('.task-priority').textContent = 
       priority === 'high' ? 'Yüksek Öncelik' :
       priority === 'medium' ? 'Orta Öncelik' : 'Düşük Öncelik';
     
     // Category
     const category = document.getElementById('edit-task-category').value;
     currentTaskCard.dataset.category = category;
     currentTaskCard.querySelector('.task-category').textContent = 
       category === 'work' ? 'İş' :
       category === 'personal' ? 'Kişisel' :
       category === 'shopping' ? 'Alışveriş' :
       category === 'study' ? 'Eğitim' : 'Sağlık';
   }
   
   closeEditModal();
 });
 
 // Close modal on outside click
 window.addEventListener('click', e => {
   if(e.target === editModal) closeEditModal();
 });
 
 // Close button
 closeBtn.addEventListener('click', closeEditModal);
 
 // Edit buttons
 document.querySelectorAll('.edit-btn').forEach(btn => {
   btn.addEventListener('click', e => {
     openEditModal(e.target.closest('.task-card'));
   });
 });