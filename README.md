# django-page_view_log
Simple page-view logging to help with forensics

Records datetime, user, session_key, ip_address, user_agent, url, view_name, gen_time, and response status_code.
This app also provides some very specific request-response caching. If a request comes in that's *identical* to one that's already being processed (same user, same post data, same everything); then this middleware will return a copy of the response object from the first request, rather than re-crunching a new response. This helps to reduce server load when a user re-clicks on a slow-loading resource, and helps to prevent double-click submission events when submitting form data.
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


