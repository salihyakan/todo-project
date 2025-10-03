@echo off
chcp 65001 >nul
echo ====================================
echo 🧪 KEDO App - Complete Test Suite
echo ====================================

echo 1. Applying critical model fixes...
echo 2. Running Complete Test Suite...

python manage.py test user_profile.tests --keepdb
python manage.py test todo.tests --keepdb  
python manage.py test notes.tests --keepdb
python manage.py test dashboard.tests --keepdb
python manage.py test tools.tests --keepdb
python manage.py test analytics.tests --keepdb

echo ✅ Complete test suite completed!
echo 📊 Test results will show above...
pause