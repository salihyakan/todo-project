from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes_categories')
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    color = models.CharField(max_length=7, default='#6f42c1', verbose_name="Renk Kodu")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'name']
        verbose_name_plural = "Kategoriler"
        indexes = [
            models.Index(fields=['user', 'name']),  # Yeni index
            models.Index(fields=['slug']),  # Yeni index
        ]

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Note(models.Model):
    PRIORITY_CHOICES = [
        ('H', 'Yüksek'),
        ('M', 'Orta'),
        ('L', 'Düşük'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=200, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategori")
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M', verbose_name="Öncelik")
    related_date = models.DateTimeField(null=True, blank=True, verbose_name="İlişkili Tarih")
    is_pinned = models.BooleanField(default=False, verbose_name="Sabitlenmiş")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Task ilişkisi - related_name değiştirildi
    task = models.ForeignKey('todo.Task', on_delete=models.CASCADE, null=True, blank=True, 
                           verbose_name="İlişkili Görev", related_name='notes')
    
    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        verbose_name = 'Not'
        verbose_name_plural = 'Notlar'
        indexes = [
            models.Index(fields=['user', 'created_at']),  # Yeni index
            models.Index(fields=['user', 'updated_at']),  # Yeni index
            models.Index(fields=['is_pinned']),  # Yeni index
            models.Index(fields=['priority']),  # Yeni index
            models.Index(fields=['user', 'category']),  # Yeni index
            models.Index(fields=['user', 'task']),  # Yeni index
            models.Index(fields=['user', 'is_pinned', 'updated_at']),  # Composite index
        ]

    def __str__(self):
        return self.title
    
    @property
    def priority_color(self):
        """Önceliğe göre renk döndürür"""
        colors = {
            'H': '#dc3545',  # Kırmızı
            'M': '#ffc107',  # Sarı
            'L': '#0dcaf0',  # Mavi
        }
        return colors.get(self.priority, '#6f42c1')