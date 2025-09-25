import environ
import os
from pathlib import Path
from django.db.backends.signals import connection_created
import matplotlib


matplotlib.use('Agg')

# Başlangıç ortam değişkenleri
env = environ.Env(
    # Varsayılan değerleri burada tanımlayın
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['localhost', '127.0.0.1']),
    REDIS_HOST=(str, 'localhost'),
    REDIS_PORT=(int, 6379),
    CELERY_BROKER_URL=(str, 'redis://localhost:6379/0'),
    CELERY_RESULT_BACKEND=(str, 'redis://localhost:6379/0'),
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# .env dosyasını oku (eğer varsa)
ENV_PATH = BASE_DIR / '.env'
if os.path.exists(ENV_PATH):
    # Daha güvenli şekilde oku
    env.read_env(ENV_PATH, overwrite=True)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/


# Yerine bu kodu ekleyin:
SECRET_KEY = env('SECRET_KEY', default='django-insecure-geçici-bir-anahtar')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])


# Application definition
BASE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MY_APPS = [
    'dashboard.apps.DashboardConfig',  
    'todo.apps.TodoConfig',
    'user_profile.apps.UserProfileConfig',
    'notes.apps.NotesConfig',
    'analytics.apps.AnalyticsConfig'
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'django_celery_beat',
]

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + MY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "user_profile.context_processors.badge_notifications",
                "user_profile.context_processors.notifications",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_DIRS = [BASE_DIR / "static"]



MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
]

# Login/Logout URLs
LOGIN_URL = "user_profile:login"
LOGIN_REDIRECT_URL = "dashboard:home"
LOGOUT_REDIRECT_URL = "user_profile:login"

# CORS Settings
CORS_ALLOW_ALL_ORIGINS = True  # Only for development
CORS_ALLOW_CREDENTIALS = True

# Date formats
DATE_FORMAT = "Y-m-d"
DATETIME_FORMAT = "Y-m-d H:i:s (e)"



# Redis and Celery settings
REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env.int("REDIS_PORT", default=6379)
CELERY_BROKER_URL = env(
    "CELERY_BROKER_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_RESULT_BACKEND = env(
    "CELERY_RESULT_BACKEND", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/0"
)
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

IS_DOCKER = env.bool('IS_DOCKER', default=False)