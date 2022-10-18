from __future__ import unicode_literals
from datetime import timedelta

from django.db import models
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

from cron.signals import cron_daily


PAGE_VIEW_LOG_INCLUDES_ANONYMOUS = getattr(settings, 'PAGE_VIEW_LOG_INCLUDES_ANONYMOUS', False)

class UserAgent(models.Model):
    user_agent_hash = models.CharField(max_length=32, db_index=True)
    user_agent_string = models.TextField()

    def __str__(self):
        return self.user_agent_hash

    def __unicode__(self):
        return self.__str__()

class Url(models.Model):
    url_hash = models.CharField(max_length=32, db_index=True)
    url_string = models.TextField()

    def __str__(self):
        return u"%s" % self.url_string[:30]

    def __unicode__(self):
        return self.__str__()

class ViewName(models.Model):
    view_name_hash = models.CharField(max_length=32, db_index=True)
    view_name_string = models.TextField()

    def __str__(self):
        return u"%s" % self.view_name_string[:30]

    def __unicode__(self):
        return self.__str__()

class PageViewLog(models.Model):
    datetime = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_view_logs', on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=32, null=True, blank=True)
    ip_address = models.CharField(max_length=15)
    user_agent = models.ForeignKey(UserAgent, on_delete=models.CASCADE)

    url = models.ForeignKey(Url, on_delete=models.CASCADE)
    view_name = models.ForeignKey(ViewName, on_delete=models.CASCADE)
    gen_time = models.BigIntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    def gen_time_in_seconds(self):
        return "%s seconds" % (self.gen_time / 1000000.0)

    def gen_time_in_milliseconds(self):
        return "%sms" % (self.gen_time / 1000.0)

    # In case we use these methods within admin as list_display fields: make them sortable.
    gen_time_in_seconds.admin_order_field = 'gen_time'
    gen_time_in_milliseconds.admin_order_field = 'gen_time'

def cleanup_old_logs(**kwargs):
    # By default, django will need to load the results into memory in order to perform pre_delete and post_delete logic. We perform a 'raw' delete in order to expressly avoid this.
    # see: https://stackoverflow.com/a/36935536/341329

    # Note: It's not efficient to query by timestamp directly, because it is not indexed.
    cache_key = "page_view_log.models.cleanup_old_logs:last_id"
    earliest_id = cache.get(cache_key)
    if earliest_id is None:
        # We try to avoid this query, because it may require a full table scan.
        earliest_id = PageViewLog.objects.values_list('id', flat=True).earliest('id')

    cutoff = timezone.now() - timedelta(days=90)
    for i in range(10**4):
        # we delete them 1000 at a time, to avoid needing a big lock on this table.
        qs = PageViewLog.objects.filter(id__lt=earliest_id + 1000).values_list('id', 'datetime')
        qs = list(qs)

        if not qs:
            # We got an empty list. That's unexpected.
            # - It's possible that there are no PageViewLogs.
            # - It's possible that our earliest_id is stale / off.
            # Let's start over from scratch next time.
            cache.delete(cache_key)
            break

        # narrow results to those that are stale.
        ids = []
        for pid, datetime in qs:
            if datetime < cutoff:
                ids.append(pid)

        if not ids:
            # We found records, but they're all still 'current'. That's ok!
            break

        temp = PageViewLog.objects.filter(id__in=ids)
        temp._raw_delete(temp.db)

        # record our progress
        earliest_id = max(ids)
        cache.set(cache_key, earliest_id, None) # cache it forever

        if len(ids) < len(qs):
            # We found some records that are still 'current'. We're done for now.
            break

    # remove orphan UserAgents
    all_ids = UserAgent.objects.all().values_list('id', flat=True)
    used_ids = PageViewLog.objects.values_list('user_agent_id', flat=True).distinct()
    ids_to_delete = set(all_ids) - set(used_ids)
    qs = UserAgent.objects.filter(id__in=ids_to_delete)
    qs._raw_delete(qs.db)

    # remove orphan Urls
    all_ids = Url.objects.all().values_list('id', flat=True)
    used_ids = PageViewLog.objects.values_list('url_id', flat=True).distinct()
    ids_to_delete = set(all_ids) - set(used_ids)
    qs = Url.objects.filter(id__in=ids_to_delete)
    qs._raw_delete(qs.db)

    # remove orphan ViewNames
    all_ids = ViewName.objects.all().values_list('id', flat=True)
    used_ids = PageViewLog.objects.values_list('view_name_id', flat=True).distinct()
    ids_to_delete = set(all_ids) - set(used_ids)
    qs = ViewName.objects.filter(id__in=ids_to_delete)
    qs._raw_delete(qs.db)

cron_daily.connect(cleanup_old_logs, dispatch_uid="cleanup_old_logs")
