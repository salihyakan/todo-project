from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from slugify import slugify

User = get_user_model()

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todo_categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#6c757d')
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Kategoriler'
        ordering = ['name']
        unique_together = ['user', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.user.username}-{self.name}")
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('todo:category_detail', args=[str(self.slug)])

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('H', 'Yüksek'),
        ('M', 'Orta'),
        ('L', 'Düşük'),
    ]
    
    STATUS_CHOICES = [
        ('todo', 'Yapılacak'),
        ('in_progress', 'Devam Ediyor'),
        ('completed', 'Tamamlandı'),
        ('overdue', 'Süresi Geçmiş'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateTimeField()
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(
        'Category', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='tasks'
    )

    class Meta:
        ordering = ['-due_date']
        verbose_name_plural = 'Görevler'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('todo:task_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        # Süresi geçmiş görevleri kontrol et
        if self.due_date < timezone.now() and self.status not in ['completed', 'overdue']:
            self.status = 'overdue'
        
        # Tamamlama tarihi kontrolü
        if self.status == 'completed' and not self.completed_at:
            self.completed_at = timezone.now()
        elif self.status != 'completed' and self.completed_at:
            self.completed_at = None
            
        super().save(*args, **kwargs)

    @property
    def is_completed(self):
        return self.status == 'completed'

    @property
    def is_overdue(self):
        return self.due_date < timezone.now() and not self.is_completed

    @property
    def time_remaining(self):
        """Kalan süreyi hesapla"""
        now = timezone.now()
        if self.due_date > now:
            delta = self.due_date - now
            if delta.days > 0:
                return f"{delta.days} gün"
            elif delta.seconds // 3600 > 0:
                return f"{delta.seconds // 3600} saat"
            else:
                return f"{delta.seconds // 60} dakika"
        else:
            return "Süresi doldu"

    @property
    def is_almost_due(self):
        """24 saat içinde bitecek mi?"""
        now = timezone.now()
        return (self.due_date - now).total_seconds() < 86400 and not self.is_completed and not self.is_overdue

    @property
    def notes_count(self):
        """Bu göreve ait not sayısı"""
        return self.notes.count()