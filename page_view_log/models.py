from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings

from cron.signals import cron_daily

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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='page_view_logs')
    session_key = models.CharField(max_length=32)
    ip_address = models.CharField(max_length=15)
    user_agent = models.ForeignKey(UserAgent)

    url = models.ForeignKey(Url)
    view_name = models.ForeignKey(ViewName)
    gen_time = models.BigIntegerField(null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)

    def gen_time_in_seconds(self):
        return "%s seconds" % (self.gen_time / 1000000.0)

    def gen_time_in_milliseconds(self):
        return "%sms" % (self.gen_time / 1000.0)

def cleanup_old_logs(**kwargs):
    # By default, django will need to load the results into memory in order to perform pre_delete and post_delete logic. We perform a 'raw' delete in order to expressly avoid this.
    # see: https://stackoverflow.com/a/36935536/341329

    qs = PageViewLog.objects.filter(datetime__lt=datetime.now()-timedelta(days=90))
    qs._raw_delete(qs.db)

    # remove orphan UserAgents
    user_agent_ids = PageViewLog.objects.values_list('user_agent_id', flat=True).distinct()
    user_agent_ids = list(user_agent_ids)
    qs = UserAgent.objects.exclude(id__in=user_agent_ids)
    qs._raw_delete(qs.db)

    # remove orphan Urls
    url_ids = PageViewLog.objects.values_list('url_id', flat=True).distinct()
    url_ids = list(url_ids)
    qs = Url.objects.exclude(id__in=url_ids)
    qs._raw_delete(qs.db)

    # remove orphan ViewNames
    view_name_ids = PageViewLog.objects.values_list('view_name_id', flat=True).distinct()
    view_name_ids = list(view_name_ids)
    qs = ViewName.objects.exclude(id__in=view_name_ids)
    qs._raw_delete(qs.db)

cron_daily.connect(cleanup_old_logs, dispatch_uid="cleanup_old_logs")
