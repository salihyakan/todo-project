from django import forms
from .models import Note, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'priority', 'related_date', 'is_pinned']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'related_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)