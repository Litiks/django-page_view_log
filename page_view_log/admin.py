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

class PageViewLogAdmin(admin.ModelAdmin):
    search_fields = ('user__email','ip_address','url__url_string')
    ordering = ('-datetime',)

    list_display = ('datetime', 'user', 'status_code','url', 'view_name','gen_time_in_milliseconds','ip_address', 'user_agent')
    list_filter = ('status_code','view_name','user__email')

admin.site.register(UserAgent, UserAgentAdmin)
#admin.site.register(Url, UrlAdmin)
#admin.site.register(ViewName, ViewNameAdmin)
admin.site.register(PageViewLog, PageViewLogAdmin)
