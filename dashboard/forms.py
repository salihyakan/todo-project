# dashboard/forms.py
from django import forms
from .models import CalendarEvent

class CalendarEventForm(forms.ModelForm):
    # Hatırlatıcı alanını kaldırıyoruz
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'start_date', 'end_date', 'event_type']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Etkinlik başlığı',
                'maxlength': '50'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Etkinlik açıklaması'
            }),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'event_type': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Sadece etkinlik ve hatırlatıcı seçeneklerini göster
        self.fields['event_type'].choices = [
            ('event', 'Etkinlik'),
            ('reminder', 'Hatırlatıcı')
        ]