
```
TODO
├─ analytics
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_useranalytics_analytics_u_product_77ede4_idx_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ static
│  │  └─ analytics
│  ├─ templates
│  │  └─ analytics
│  │     ├─ dashboard.html
│  │     └─ stats_badge.html
│  ├─ tests.py
│  ├─ urls.py
│  ├─ utils.py
│  ├─ views.py
│  └─ __init__.py
├─ config
│  ├─ asgi.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ __init__.py
├─ dashboard
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ management
│  │  └─ commands
│  │     └─ update_all_stats.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_pomodorosession.py
│  │  ├─ 0003_alter_pomodorosession_options_and_more.py
│  │  ├─ 0004_alter_calendarevent_options_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ templates
│  │  └─ dashboard
│  │     ├─ calendar.html
│  │     ├─ contact.html
│  │     ├─ cookies.html
│  │     ├─ day_detail.html
│  │     ├─ event_detail.html
│  │     ├─ faq.html
│  │     ├─ guide.html
│  │     ├─ help.html
│  │     ├─ home.html
│  │     ├─ landing_page.html
│  │     ├─ license.html
│  │     ├─ pomodoro.html
│  │     ├─ privacy.html
│  │     ├─ support.html
│  │     └─ terms.html
│  ├─ templatetags
│  │  ├─ cat_utils.py
│  │  └─ __init__.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ deploy.py
├─ lists
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ templates
│  │  └─ lists
│  │     ├─ list_confirm_delete.html
│  │     ├─ list_detail.html
│  │     ├─ list_form.html
│  │     └─ list_list.html
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ manage.py
├─ notes
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_category_notes_categ_user_id_f7e623_idx_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ templates
│  │  └─ notes
│  │     ├─ category_confirm_delete.html
│  │     ├─ category_form.html
│  │     ├─ category_list.html
│  │     ├─ note_confirm_delete.html
│  │     ├─ note_detail.html
│  │     ├─ note_form.html
│  │     ├─ note_list.html
│  │     └─ task_notes.html
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ pytest.ini
├─ quick_fix.bat
├─ README.md
├─ requirements.txt
├─ run_fixed_tests.py
├─ run_production.bat
├─ run_tests.bat
├─ static
│  ├─ css
│  │  ├─ calendar.css
│  │  ├─ cats.css
│  │  ├─ custom.css
│  │  ├─ main.css
│  │  └─ styles.css
│  ├─ images
│  │  ├─ ked-o.png
│  │  ├─ kedo-1.png
│  │  ├─ kedo-10.png
│  │  ├─ kedo-11.png
│  │  ├─ kedo-12.png
│  │  ├─ kedo-13.png
│  │  ├─ kedo-14.png
│  │  ├─ kedo-15.png
│  │  ├─ kedo-16.png
│  │  ├─ kedo-17.png
│  │  ├─ kedo-18.png
│  │  ├─ kedo-19.png
│  │  ├─ kedo-2.png
│  │  ├─ kedo-20.png
│  │  ├─ kedo-21.png
│  │  ├─ kedo-22.png
│  │  ├─ kedo-23.png
│  │  ├─ kedo-3.png
│  │  ├─ kedo-4.png
│  │  ├─ kedo-5.png
│  │  ├─ kedo-6.png
│  │  ├─ kedo-7.png
│  │  ├─ kedo-8.png
│  │  ├─ kedo-9.png
│  │  └─ logo.png
│  └─ js
│     ├─ calendar.js
│     ├─ index.global.js
│     ├─ index.global.min.js
│     ├─ notifications.js
│     ├─ pomodoro.js
│     ├─ sidebar.js
│     └─ todo.js
├─ templates
│  └─ core
│     ├─ base.html
│     ├─ footer.html
│     ├─ navbar.html
│     └─ sidebar.html
├─ test_factories.py
├─ todo
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ management
│  │  └─ commands
│  │     └─ seed_todo.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_category_todo_catego_user_id_fb6e6b_idx_and_more.py
│  │  ├─ 0003_alter_task_due_date.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ templates
│  │  └─ todo
│  │     ├─ category_confirm_delete.html
│  │     ├─ category_detail.html
│  │     ├─ category_form.html
│  │     ├─ category_list.html
│  │     ├─ task_confirm_delete.html
│  │     ├─ task_detail.html
│  │     ├─ task_form.html
│  │     └─ task_list.html
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ tools
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_alter_studynote_content.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ templates
│  │  └─ tools
│  │     ├─ calculator.html
│  │     ├─ home.html
│  │     ├─ stopwatch.html
│  │     ├─ study_notes_list.html
│  │     ├─ study_note_confirm_delete.html
│  │     ├─ study_note_detail.html
│  │     ├─ study_note_form.html
│  │     └─ timer.html
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ user_profile
│  ├─ admin.py
│  ├─ apps.py
│  ├─ backends.py
│  ├─ context_processors.py
│  ├─ forms.py
│  ├─ management
│  │  └─ commands
│  │     └─ check_all_badges.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  ├─ 0002_alter_badge_options_alter_badgetype_options_and_more.py
│  │  ├─ 0003_badge_user_profil_name_e40297_idx_and_more.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ signals.py
│  ├─ templates
│  │  └─ user_profile
│  │     ├─ badge_detail.html
│  │     ├─ badge_list.html
│  │     ├─ login.html
│  │     ├─ notifications.html
│  │     ├─ password_change.html
│  │     ├─ password_change_done.html
│  │     ├─ password_reset.html
│  │     ├─ password_reset_complete.html
│  │     ├─ password_reset_confirm.html
│  │     ├─ password_reset_done.html
│  │     ├─ password_reset_email.html
│  │     ├─ password_reset_subject.txt
│  │     ├─ profile.html
│  │     ├─ profile_edit.html
│  │     └─ register.html
│  ├─ templatetags
│  │  └─ badge_utils.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ utils.py
│  ├─ views.py
│  └─ __init__.py
└─ waitress.conf.py

```