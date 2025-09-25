from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile
from django.core.exceptions import ValidationError


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kullanıcı Adı',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifre'
        })
    )
    
    error_messages = {
        'invalid_login': "Geçersiz kullanıcı adı veya şifre.",
        'inactive': "Bu hesap aktif değil.",
    }

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
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location', 'birth_date', 'website', 'pomodoro_duration', 'daily_goal']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'pomodoro_duration': forms.NumberInput(attrs={'class': 'form-control'}),
            'daily_goal': forms.NumberInput(attrs={'class': 'form-control'}),
        }