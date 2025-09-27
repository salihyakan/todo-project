from django import forms
from .models import Note, Category

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kategori adı girin'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['title', 'content', 'category', 'priority', 'related_date', 'is_pinned', 'task']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Not başlığı girin'}),
            'content': forms.Textarea(attrs={'rows': 8, 'class': 'form-control', 'placeholder': 'Not içeriğini girin'}),
            'related_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'task': forms.Select(attrs={'class': 'form-select'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(user=user)
        self.fields['category'].required = False
        
        # Kullanıcının görevlerini getir
        from todo.models import Task
        self.fields['task'].queryset = Task.objects.filter(user=user)
        self.fields['task'].required = False
        self.fields['task'].label = "İlişkili Görev (isteğe bağlı)"