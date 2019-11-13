from __future__ import unicode_literals
from django.contrib import admin

from page_view_log.models import UserAgent, Url, ViewName, PageViewLog

class UserAgentAdmin(admin.ModelAdmin):
    search_fields = ('user_agent_hash','user_agent_string')
    ordering = ('user_agent_string',)
    list_display = ('user_agent_hash', 'user_agent_string')

class UrlAdmin(admin.ModelAdmin):
    search_fields = ('url_hash','url_string')
    ordering = ('url_string',)
    list_display = ('url_hash', 'url_string')

class ViewNameAdmin(admin.ModelAdmin):
    search_fields = ('view_name_hash','view_name_string')
    ordering = ('view_name_string',)
    list_display = ('view_name_hash', 'view_name_string')

class StatusCodeFilter(admin.SimpleListFilter):
    """ If we leave django to it's own devices; it tries to determine the unique values for this filter by querying the table (which is massive).
        Instead, we only list those codes occurring recently.
        see: https://docs.djangoproject.com/en/2.2/ref/contrib/admin/#django.contrib.admin.ModelAdmin.list_filter
    """
    title = 'status code'
    parameter_name = 'status_code'

    def lookups(self, request, model_admin):
        # this is the magic
        qs = model_admin.get_queryset(request).values_list('status_code', flat=True)[:1000]
        qs = sorted(set(qs))
        return [(n,n) for n in qs]

    def queryset(self, request, queryset):
        v = self.value()
        if v:
            return queryset.filter(status_code=v)

class PageViewLogAdmin(admin.ModelAdmin):
    search_fields = ('user__email','ip_address','url__url_string')
    ordering = ('-id',)

    list_display = ('datetime', 'user', 'status_code','url', 'view_name','gen_time_in_milliseconds','ip_address', 'user_agent')
    list_filter = (StatusCodeFilter,)

admin.site.register(UserAgent, UserAgentAdmin)
#admin.site.register(Url, UrlAdmin)
#admin.site.register(ViewName, ViewNameAdmin)
admin.site.register(PageViewLog, PageViewLogAdmin)
