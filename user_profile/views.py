from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from slugify import slugify



def login_view(request): 
    if request.user.is_authenticated:
        messages.info(request, f'{request.user.username } Daha önce giriş yapmışsın')
        return redirect('home_view')
    
    context = {}
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if len (username) < 6 or len(password) < 6:
            messages.warning(request, f'Kullanıcı adı ve şifre en az 6 karakter olmalıdır')
            return redirect('user_profile:login_view')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.info(request, f'{request.user.username } Başarıyla giriş yaptınız')
            return redirect('home_view')
    return render(request, "user_profile/login.html", context)


def logout_view(request):
    messages.info(request, f'{request.user.username } Oturum kapatıldı')
    logout(request)
    return redirect("home_view")


def register_view(request):
    context = {}
    if request.method == "POST":
        post_info = request.POST
        username = post_info.get("username")
        password = post_info.get("password")
        password_confirm = post_info.get("password_confirm")
        email = post_info.get("email")
        email_confirm = post_info.get("email_confirm")

        if len(username) < 6 or len(password) < 6 or len(email) < 6:
            messages.warning(request, f'Bilgiler en az 6 karakter olmalıdır')
            return redirect('user_profile:register_view')

        if email != email_confirm:
            messages.warning(request, f'Lütfen E-mail Bilgisini Doğru Girin')
            return redirect('user_profile:register_view')

        if password != password_confirm:
            messages.warning(request, f'Lütfen Şifreyi Doğru Girin')
            return redirect('user_profile:register_view')

        user, created = User.objects.get_or_create(username=email)
        if not created:
            user_login = authenticate(request, username=username, password=password)
            if user is not None:
                messages.success(request, f'{username} Daha önce kayıt olmuşusunuz. Ana Sayfaya yönlendirildiniz')
                login(request, user_login)
                return redirect('home_view')
            messages.warning(request, f'{username} Kullanıcı adı zaten sistemde kayıtlı. Login sayfasına yönlendiriliyorsunuz')
            return redirect('user_profile:login_view')
        
        user.email = email
        user.username = username
        user.set_password(password)

        profile, profile_created = Profile.objects.get_or_create(user=user)
        profile.slug = slugify(username)
        user.save()

        messages.success(request, f'{username} Başarıyla kayıt oldunuz.')
        user_login = authenticate(request, username=username, password=password)
        login(request, user_login)
        return redirect('home_view')


    return render(request, "user_profile/register.html", context)