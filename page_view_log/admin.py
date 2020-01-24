from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.auth import get_user_model

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
    # search_fields = ('ip_address',)
    ordering = ('-id',)

    list_display = ('datetime', 'user', 'status_code','url', 'view_name','gen_time_in_milliseconds','ip_address', 'user_agent')
    list_filter = (StatusCodeFilter,)

    def get_search_results(self, request, queryset, search_term):
        """ We do our own custom filtering; in an effort to eliminate table joins.
            This method needs to return a tuple containing a queryset modified to implement the search, and a boolean indicating if the results may contain duplicates.
            see: https://docs.djangoproject.com/en/1.11/ref/contrib/admin/#django.contrib.admin.ModelAdmin.get_search_results
        """
        words = search_term.split()
        ids = set()
        first_loop = True
        for word in words:
            qs = queryset
            found_something = False

            # user__email
            users = get_user_model().objects.filter(email__icontains=word)
            user_ids = list(users.values_list('pk', flat=True))
            if user_ids:
                found_something = True
                qs = qs.filter(user_id__in=user_ids)

            # url__url_string
            urls = Url.objects.filter(url_string__icontains=word)
            url_ids = list(urls.values_list('pk', flat=True))
            if url_ids:
                found_something = True
                qs = qs.filter(url_id__in=url_ids)

            # view_name__view_name_string
            view_names = ViewName.objects.filter(view_name_string__icontains=word)
            view_name_ids = list(view_names.values_list('pk', flat=True))
            if view_name_ids:
                found_something = True
                qs = qs.filter(view_name_id__in=view_name_ids)

            if not found_something:
                # There are no results for this word. That's it. We're done.
                return queryset.none()

            if len(words) == 1:
                # We can skip a little work since there's only one search term.
                return qs, False

            if first_loop:
                ids.update(set(qs.values_list('pk', flat=True)))
            else:
                # we only keep results that match ALL search terms
                ids.intersection_update(set(qs.values_list('pk', flat=True)))
            first_loop = False

        queryset = queryset.filter(id__in=ids)
        return queryset, False

admin.site.register(UserAgent, UserAgentAdmin)
# admin.site.register(Url, UrlAdmin)
# admin.site.register(ViewName, ViewNameAdmin)
admin.site.register(PageViewLog, PageViewLogAdmin)
