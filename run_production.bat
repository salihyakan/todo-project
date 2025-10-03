@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 KEDO App - Production Server (Windows)
echo ========================================

set DJANGO_SETTINGS_MODULE=config.settings
set WAITRESS_HOST=0.0.0.0
set WAITRESS_PORT=8000
set WAITRESS_THREADS=8

echo 📁 Creating logs directory...
if not exist logs mkdir logs

echo 🔍 Checking Django configuration...
python manage.py check --deploy

echo 📦 Collecting static files...
python manage.py collectstatic --noinput

echo 🗃️ Applying database migrations...
python manage.py migrate

echo 🚀 Starting Waitress production server...
echo 📍 Server: http://%WAITRESS_HOST%:%WAITRESS_PORT%
echo ⏰ Started at: %date% %time%
echo ========================================

waitress-serve --host=%WAITRESS_HOST% --port=%WAITRESS_PORT% --threads=%WAITRESS_THREADS% --channel-timeout=300 --connection-limit=1000 config.wsgi:application

pause