from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls"))
)
