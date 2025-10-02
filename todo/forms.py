from django import forms
from .models import Task, Category
from django.utils import timezone
from django.core.exceptions import ValidationError

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean_name(self):
        name = self.cleaned_data['name']
        if Category.objects.filter(user=self.user, name__iexact=name).exists():
            if not self.instance or self.instance.name.lower() != name.lower():
                raise ValidationError('Bu isimde bir kategori zaten var.')
        return name

class TaskForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yeni kategori adı',
            'id': 'new-category-input'
        }),
        label='Veya yeni kategori oluştur'
    )
    
    class Meta:
        model = Task
        fields = ['title', 'description', 'due_date', 'priority', 'status', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'due_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local', 'class': 'form-control'},
                format='%Y-%m-%dT%H:%M'
            ),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select', 'id': 'category-select'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Yeni görev oluşturulurken 'completed' seçeneğini kaldır
        if not self.instance.pk:
            self.fields['status'].choices = [
                ('todo', 'Yapılacak'),
                ('in_progress', 'Devam Ediyor'),
            ]
        
        if self.user:
            self.fields['category'].queryset = Category.objects.filter(user=self.user)
            
            if not self.instance.pk:
                # SADECE BU SATIRI DEĞİŞTİRİYORUZ - Yerel saat için
                now_local = timezone.localtime(timezone.now())
                self.fields['due_date'].initial = now_local.strftime('%Y-%m-%dT%H:%M')
    
    def clean_due_date(self):
        # YENİ METOT EKLİYORUZ - Timezone düzeltmesi için
        due_date = self.cleaned_data.get('due_date')
        if due_date and timezone.is_naive(due_date):
            # Naive datetime'ı timezone-aware yap
            due_date = timezone.make_aware(due_date, timezone.get_current_timezone())
        return due_date
    
    def clean(self):
        cleaned_data = super().clean()
        new_category = cleaned_data.get('new_category')
        category = cleaned_data.get('category')
        
        if new_category and category:
            raise forms.ValidationError('Lütfen ya mevcut bir kategori seçin ya da yeni bir kategori adı girin, ikisini birden değil.')
        
        if not new_category and not category:
            raise forms.ValidationError('Lütfen bir kategori seçin veya yeni kategori adı girin.')
        
        if new_category:
            # Yeni kategori oluştur
            category, created = Category.objects.get_or_create(
                user=self.user,
                name=new_category,
                defaults={'color': '#6c757d'}
            )
            cleaned_data['category'] = category
        
        return cleaned_data