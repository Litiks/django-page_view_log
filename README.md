# django-page_view_log
Simple page-view logging to help with forensics

Records datetime, user, session_key, ip_address, user_agent, url, view_name, gen_time, and response status_code.
If you have django-cron installed, logs will automatically be purged after 90 days.


Install
-------

- using pip: `pip install https://github.com/Litiks/django-page_view_log/archive/master.zip`
- or: add to your requirements.txt: `-e git+https://github.com/Litiks/django-page_view_log.git#egg=django-page_view_log`
- or: copy the 'page_view_log' folder to your python working directory


Integrate
---------

1. Add 'page_view_log' to your settings.INSTALLED_APPS
2. Add `'page_view_log.middleware.PageViewLogMiddleware',` to your settings.MIDDLEWARE_CLASSES, after django's built-in middleware.


