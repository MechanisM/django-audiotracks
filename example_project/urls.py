from django.conf import settings
from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     (r'^$', 'main.views.index'),
    url("^music", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
    (r'^login$', 'django.contrib.auth.views.login'),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': settings.MEDIA_ROOT}),
    )
