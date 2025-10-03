#!/usr/bin/env python
"""
KEDO App Deployment Script
Kullanım: python deploy.py [development|production]
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Komutu çalıştır ve sonucunu kontrol et"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} tamamlandı")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} başarısız: {e}")
        print(f"Stderr: {e.stderr}")
        return False

def deploy_development():
    """Development ortamı için deployment"""
    print("🚀 Development ortamı deploy ediliyor...")
    
    commands = [
        ("python manage.py check", "Django kontrolü"),
        ("python manage.py migrate", "Database migrations"),
        ("python manage.py runserver 8080", "Development server başlatılıyor")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    print("🎉 Development sunucusu http://localhost:8080 adresinde çalışıyor")
    return True

def deploy_production():
    """Production ortamı için deployment"""
    print("🚀 Production ortamı deploy ediliyor...")
    
    commands = [
        ("python manage.py check", "Django kontrolü"),
        ("python manage.py migrate", "Database migrations"),
        ("python manage.py collectstatic --noinput", "Static dosyalar toplanıyor"),
        ("waitress-serve --host=0.0.0.0 --port=8080 --threads=4 config.wsgi:application", "Production server başlatılıyor")
    ]
    
    for cmd, desc in commands:
        if not run_command(cmd, desc):
            return False
    
    print("🎉 Production sunucusu http://localhost:8080 adresinde çalışıyor")
    return True

def main():
    if len(sys.argv) != 2:
        print("Kullanım: python deploy.py [development|production]")
        sys.exit(1)
    
    environment = sys.argv[1].lower()
    
    if environment == "development":
        deploy_development()
    elif environment == "production":
        deploy_production()
    else:
        print("Geçersiz ortam. 'development' veya 'production' kullanın.")
        sys.exit(1)

if __name__ == "__main__":
    main()