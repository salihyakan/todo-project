
```
TODO
├─ analytics
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ signals.py
│  ├─ static
│  │  └─ analytics
│  ├─ templates
│  │  └─ analytics
│  │     ├─ dashboard.html
│  │     └─ stats_badge.html
│  ├─ templatetags
│  │  └─ analytics_tags.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ utils.py
│  ├─ views.py
│  └─ __init__.py
├─ config
│  ├─ asgi.py
│  ├─ celery.py
│  ├─ settings.py
│  ├─ urls.py
│  ├─ wsgi.py
│  └─ __init__.py
├─ dashboard
│  ├─ admin.py
│  ├─ apps.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ redis_utils.py
│  ├─ signals.py
│  ├─ tasks.py
│  ├─ templates
│  │  └─ dashboard
│  │     ├─ calendar.html
│  │     ├─ day_detail.html
│  │     ├─ event_detail.html
│  │     ├─ home.html
│  │     └─ pomodoro.html
│  ├─ templatetags
│  │  └─ dashboard_filters.py
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ docker-compose.yml
├─ Dockerfile
├─ manage.py
├─ notes
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ signals.py
│  ├─ templates
│  │  └─ notes
│  │     ├─ category_confirm_delete.html
│  │     ├─ category_form.html
│  │     ├─ category_list.html
│  │     ├─ note_confirm_delete.html
│  │     ├─ note_detail.html
│  │     ├─ note_form.html
│  │     └─ note_list.html
│  ├─ tests.py
│  ├─ urls.py
│  ├─ views.py
│  └─ __init__.py
├─ README.md
├─ requirements.txt
├─ static
│  ├─ css
│  │  ├─ calendar.css
│  │  ├─ custom.css
│  │  └─ styles.css
│  └─ js
│     ├─ calendar.js
│     ├─ index.global.js
│     ├─ index.global.min.js
│     ├─ notifications.js
│     ├─ pomodoro.js
│     └─ todo.js
├─ templates
│  └─ core
│     ├─ base.html
│     ├─ footer.html
│     └─ navbar.html
├─ todo
│  ├─ admin.py
│  ├─ apps.py
│  ├─ forms.py
│  ├─ management
│  │  └─ commands
│  │     └─ seed_todo.py
│  ├─ migrations
│  │  ├─ 0001_initial.py
│  │  └─ __init__.py
│  ├─ models.py
│  ├─ signals.py
│  ├─ tasks.py
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
└─ user_profile
   ├─ admin.py
   ├─ apps.py
   ├─ backends.py
   ├─ context_processors.py
   ├─ forms.py
   ├─ migrations
   │  ├─ 0001_initial.py
   │  └─ __init__.py
   ├─ models.py
   ├─ signals.py
   ├─ tasks.py
   ├─ templates
   │  └─ user_profile
   │     ├─ badge_detail.html
   │     ├─ badge_list.html
   │     ├─ login.html
   │     ├─ notifications.html
   │     ├─ password_change.html
   │     ├─ password_change_done.html
   │     ├─ password_reset.html
   │     ├─ password_reset_complete.html
   │     ├─ password_reset_confirm.html
   │     ├─ password_reset_done.html
   │     ├─ password_reset_email.html
   │     ├─ password_reset_subject.txt
   │     ├─ profile.html
   │     ├─ profile_edit.html
   │     └─ register.html
   ├─ templatetags
   │  └─ badge_utils.py
   ├─ tests.py
   ├─ urls.py
   ├─ views.py
   └─ __init__.py

```