# tools/forms.py
from django import forms
from tinymce.widgets import TinyMCE
from .models import StudyNote

class StudyNoteForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCE(
            attrs={
                'cols': 80, 
                'rows': 30,
                'class': 'form-control'
            }
        ),
        label='İçerik'
    )
    
    class Meta:
        model = StudyNote
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control form-control-lg',
                'placeholder': 'Not başlığını giriniz...',
                'style': 'font-size: 1.2rem; padding: 15px;'
            }),
        }
        labels = {
            'title': 'Başlık',
            'content': 'İçerik'
        }