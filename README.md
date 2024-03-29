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
3. Add `PAGE_VIEW_LOG_INCLUDES_ANONYMOUS = True` if PageViewLog.user should allow None.
4. Add `PAGE_VIEW_LOG_NO_DIBS_PATHS = [*path_patterns]` to skip the dibs logic when path matches a given string (exactly) or regular expression
5. Add `PAGE_VIEW_LOG_FLUSH_IN_BATCHES = True`, for an improvement to DB inserts, at the risk of losing the last few logs at server shutdown.


Example
-------

```python
# settings.py

import re

INSTALLED_APPS = [..., 'page_view_log', ...]
MIDDLEWARE_CLASSES = [..., 'page_view_log.middleware.PageViewLogMiddleware', ...]
PAGE_VIEW_LOG_INCLUDES_ANONYMOUS = True
PAGE_VIEW_LOG_NO_DIBS_PATHS = [
    '/api/',               # exact, i.e. doesn't match '/api/get_user/'
    re.compile('^/api/'),  # starts with
]
PAGE_VIEW_LOG_FLUSH_IN_BATCHES = True
```
