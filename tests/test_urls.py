from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url("^music", include("audiotracks.urls")),
    url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
)
