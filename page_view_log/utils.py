from collections import deque
from datetime import timedelta
from threading import local

from django.utils import timezone

from page_view_log.models import PageViewLog

class PageViewLogQueue(local):
    """ a thread local queue """
    def __init__(self, *args, **kwargs):
        self.queue = deque()
        self.last_flush = timezone.now()

    def append(self, page_view_log):
        self.queue.append(page_view_log)

    def conditional_flush(self):
        if self.last_flush < timezone.now() - timedelta(seconds=5):
            # Let's flush to the database.
            batch = []
            while self.queue:
                batch.append(self.queue.popleft())

            try:
                PageViewLog.objects.bulk_create(batch)
            except Exception as e:
                print("An error occurred saving the PageViewLog: '{}'".format(e))
            self.last_flush = timezone.now()

page_view_log_queue = PageViewLogQueue()
