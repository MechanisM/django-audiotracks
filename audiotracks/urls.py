from django.conf.urls.defaults import *
from audiotracks import feeds

urlpatterns = patterns("audiotracks.views",
    url("^/?$", "index", name="audiotracks"),
    url("^/track/(?P<track_slug>.*)$", "track_detail", name="track_detail"),
    url("^/upload", "upload_track", name="upload_track"),
    url("^/edit/(?P<track_id>.+)", "edit_track", name="edit_track"),
    url("^/confirm_delete/(?P<track_id>\d+)$", "confirm_delete_track", 
        name="confirm_delete_track"),
    url("^/delete$", "delete_track", name="delete_track"),
    url("^/tracks$", "user_index", name="user_index"),
    url("^/feed/?$", feeds.AllTracks(), name="all_tracks_feed"),
    url("^/user_feed/?$", feeds.UserTracks(),
        name="user_tracks_feed"),
)
