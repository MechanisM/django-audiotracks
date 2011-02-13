from django.conf.urls.defaults import *

urlpatterns = patterns("audiotracks.views",
    url("^$", "index", name="audiotracks"),
    url("^/track/(?P<track_slug>.*)$", "track_detail", name="track_detail"),
    url("^/upload_track", "upload_track", name="upload_track"),
    url("^/edit_track/(?P<track_id>.+)", "edit_track", name="edit_track"),
    url("^/tracks$", "user_index", name="user_index"),
)
