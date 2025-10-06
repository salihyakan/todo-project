from django import forms
from .models import List, ListItem
from django.utils import timezone

class ListForm(forms.ModelForm):
    class Meta:
        model = List
        fields = ['title', 'description', 'list_type', 'color', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Liste başlığını girin...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Liste açıklaması (isteğe bağlı)...'
            }),
            'list_type': forms.Select(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'type': 'color',
                'style': 'width: 60px; height: 38px; padding: 2px; cursor: pointer;'
            }),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Color field için varsayılan değer
        if not self.instance.pk and not self.data.get('color'):
            self.initial['color'] = '#FFD700'

class ListItemForm(forms.ModelForm):
    class Meta:
        model = ListItem
        fields = ['content', 'priority', 'due_date']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Yapılacak maddeyi girin...'
            }),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
        }
    
    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and due_date < timezone.now():
            raise forms.ValidationError("Son tarih geçmiş bir tarih olamaz!")
        return due_date

class QuickAddItemForm(forms.ModelForm):
    class Meta:
        model = ListItem
        fields = ['content']
        widgets = {
            'content': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Hızlı ekle...',
                'style': 'flex-grow: 1;'
            })
        }