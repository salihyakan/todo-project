from django.db import models
from django.contrib.auth.models import User

class StudyNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Kullanıcı")
    title = models.CharField(max_length=200, verbose_name="Başlık")
    content = models.TextField(verbose_name="İçerik")  # Geçici olarak TextField
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Çalışma Notu'
        verbose_name_plural = 'Çalışma Notları'
    
    def __str__(self):
        return self.title