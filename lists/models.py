from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

class List(models.Model):
    LIST_TYPES = [
        ('shopping', '🛒 Alışveriş Listesi'),
        ('todo', '✅ Yapılacaklar Listesi'),
        ('work', '💼 İş Listesi'),
        ('personal', '🎯 Kişisel Liste'),
        ('custom', '📝 Özel Liste'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_lists')
    title = models.CharField(max_length=200, verbose_name='Liste Başlığı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    list_type = models.CharField(max_length=20, choices=LIST_TYPES, default='custom', verbose_name='Liste Türü')
    color = models.CharField(max_length=7, default='#FFD700', verbose_name='Renk Kodu')  # Sarı tonları
    is_pinned = models.BooleanField(default=False, verbose_name='Sabitlenmiş')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['user', 'list_type']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def get_absolute_url(self):
        return reverse('lists:list_detail', kwargs={'pk': self.pk})
    
    def completed_items_count(self):
        return self.items.filter(completed=True).count()
    
    def total_items_count(self):
        return self.items.count()
    
    def progress_percentage(self):
        total = self.total_items_count()
        if total == 0:
            return 0
        return int((self.completed_items_count() / total) * 100)
    def save(self, *args, **kwargs):
        # Liste her kaydedildiğinde updated_at güncellenir
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class ListItem(models.Model):
    PRIORITY_CHOICES = [
        ('low', '🔽 Düşük'),
        ('medium', '🔼 Orta'),
        ('high', '⏫ Yüksek'),
        ('urgent', '🚨 Acil'),
    ]
    
    list = models.ForeignKey(List, on_delete=models.CASCADE, related_name='items')
    content = models.CharField(max_length=500, verbose_name='Madde İçeriği')
    completed = models.BooleanField(default=False, verbose_name='Tamamlandı')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium', verbose_name='Öncelik')
    due_date = models.DateTimeField(null=True, blank=True, verbose_name='Son Tarih')
    order = models.PositiveIntegerField(default=0, verbose_name='Sıra')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'created_at']
        indexes = [
            models.Index(fields=['list', 'completed']),
            models.Index(fields=['list', 'priority']),
            models.Index(fields=['due_date']),
        ]
    
    def __str__(self):
        status = "✓" if self.completed else "○"
        return f"{status} {self.content}"
    
    def is_overdue(self):
        if self.due_date and not self.completed:
            return self.due_date < timezone.now()
        return False
    
    def days_until_due(self):
        if self.due_date:
            delta = self.due_date - timezone.now()
            return delta.days
        return None
    
    def save(self, *args, **kwargs):
        # Madde kaydedildiğinde listeyi güncelle
        if self.list:
            self.list.updated_at = timezone.now()
            self.list.save()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        # Madde silindiğinde listeyi güncelle
        list_obj = self.list
        super().delete(*args, **kwargs)
        if list_obj:
            list_obj.updated_at = timezone.now()
            list_obj.save()