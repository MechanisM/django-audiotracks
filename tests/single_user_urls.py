from django.conf.urls.defaults import *

urlpatterns = patterns("",
    url("^music", include("audiotracks.urls")),
)
