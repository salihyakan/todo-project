from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError

class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-posta adresiniz',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifreniz'
        })
    )
    
    error_messages = {
        'invalid_login': "Geçersiz e-posta adresi veya şifre.",
        'inactive': "Bu hesap aktif değil.",
    }

class LoginForm(EmailAuthenticationForm):
    pass

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'E-posta adresiniz'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kullanıcı adınız'
        })
    )
    password1 = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifreniz'
        })
    )
    password2 = forms.CharField(
        label='Şifre Onayı',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifrenizi tekrar girin'
        })
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Bu kullanıcı adı zaten alınmış.')
        return username

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ProfileUpdateForm(forms.ModelForm):
    # Profil resmi alanını özelleştir - "Currently" yazısını kaldır
    profile_picture = forms.ImageField(
        label='Profil Resmi',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        })
    )
    
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'website', 'pomodoro_duration', 'daily_goal']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Kendinizden kısaca bahsedin...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://ornek.com'
            }),
            'pomodoro_duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 5,
                'max': 60
            }),
            'daily_goal': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 20
            }),
        }
        labels = {
            'profile_picture': 'Profil Resmi',
            'bio': 'Hakkımda',
            'website': 'Web Sitesi',
            'pomodoro_duration': 'Pomodoro Süresi',
            'daily_goal': 'Günlük Hedef',
        }