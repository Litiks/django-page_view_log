from collections import deque
from datetime import timedelta
import heapq
from threading import local
import time
import random

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


class MyLRUCache:
    """ a simple dictionary LRU cache """
    def __init__(self):
        self.data = {
            # key: (value, timestamp_of_last_use),
        }
        self.cache_size = 5000     # Number of keys to store. Adjusting this will change the total memory used.

    def get(self, key):
        if key in self.data:
            # record this use (access).
            self.data[key][1] = time.time()
            return self.data[key][0]

    def set(self, key, value):
        if len(self.data) > self.cache_size:
            # let's make room.
            self.evict()

        self.data[key] = [value, time.time()]

    def evict(self):
        # We want to evict those elements in the dictionary that haven't been used recently.
        # Ideally, we want to do this without taking a long time.. so it'd be nice to not access the entire dictionary
        # But we're talking about stuff that's sitting in memory.. so performance shouldn't be *that* bad.

        num_to_evict = len(self.data) - int(self.cache_size * 0.95)

        # because we'll be sorting items later, let's just take a random sample of the full cache.
        sample_size = min(
            num_to_evict * 5,  # we take 5x the num_to_evict, so that we're reasonably confident we're finding some older records.
            len(self.data),
        )
        options = random.sample(
            list(self.data.items()),
            k = sample_size,
        )

        # re-order each option to the format: (timestamp, key)
        options = [(v[1], k) for k,v in options]

        # 'heapify' the list of eviction options
        # Using a 'heap' is more efficient than sorting the entire dataset.
        # - It's O(n) to heapify
        # - It's O(log n) to pull out the smallest value
        # - So, in total, it's O(100 log n) to pull out the 100 smallest values
        #     - (Which is **much** faster than O(n log n) to sort the whole list)
        # see: https://docs.python.org/3/library/heapq.html#heapq.heapify
        heapq.heapify(options)
        for i in range(num_to_evict):
            timestamp, key = heapq.heappop(options)
            del self.data[key]

my_lru_cache = MyLRUCache()
