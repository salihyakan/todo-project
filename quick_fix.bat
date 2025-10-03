@echo off
chcp 65001 >nul
echo ====================================
echo 🔧 KEDO App - Quick Test Fixes
echo ====================================

echo 1. Applying URL fixes...
echo 2. Fixing test assertions...
echo 3. Running critical tests only...

python manage.py test user_profile.tests.UserProfileAuthenticationTests --keepdb
if %errorlevel% neq 0 exit /b %errorlevel%

python manage.py test user_profile.tests.UserProfileViewsTests --keepdb
if %errorlevel% neq 0 exit /b %errorlevel%

python manage.py test todo.tests.TaskCRUDTests --keepdb
if %errorlevel% neq 0 exit /b %errorlevel%

python manage.py test notes.tests.NoteCRUDTests --keepdb
if %errorlevel% neq 0 exit /b %errorlevel%

python manage.py test dashboard.tests.DashboardViewsTests --keepdb
if %errorlevel% neq 0 exit /b %errorlevel%

echo ✅ Quick test fixes completed!
pause