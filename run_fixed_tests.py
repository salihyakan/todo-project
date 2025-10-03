#!/usr/bin/env python
"""
KEDO App - Fixed Test Runner
Bu script, düzeltilmiş test senaryolarını çalıştırmak için kullanılır.
"""
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()
    
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, failfast=False)
    
    # Sadece belirli testleri çalıştır
    tests = [
        'user_profile.tests.UserProfileAuthenticationTests',
        'user_profile.tests.UserProfileViewsTests',
        'todo.tests.TaskCRUDTests',
        'notes.tests.NoteCRUDTests',
        'dashboard.tests.DashboardViewsTests',
    ]
    
    print("🧪 Running fixed test suites...")
    failures = test_runner.run_tests(tests)
    if failures:
        print(f"❌ {failures} test(s) failed.")
    else:
        print("✅ All tests passed!")
    sys.exit(bool(failures))