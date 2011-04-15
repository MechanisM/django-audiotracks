==================
django-audiotracks
==================

A pluggable Django_ app to publish audio tracks.

Introduction
~~~~~~~~~~~~

django-audiotracks is a simple reusable Django_ application that allow users to
publish audio tracks on your web site. It provides a Track model, a set of
views, default templates and sensible defaut URL configuration.  It uses
mutagen_ to extract metadata from the audio files and prefill track attributes.
PIL is also required to process the image that can be attached to a track.  

A basic example_project is provided with the source code.

Installation
~~~~~~~~~~~~

Install the ``audiotracks`` package in your Python path. A ``setup.py`` script is provided. You
can use it with a command such as::

    $ python setup.py develop

Mount the app in your root ROOT_URLCONF_ by adding a piece of code similar to::


    urlpatterns += patterns('',
        # In the example we mount the app under /music. Feel free to use
        # something else
        url("^music", include("audiotracks.urls")),
        url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
    )

Edit ``settings.py`` and add ``'audiotracks`` to your list of
``INSTALLED_APPS``. Then synchronize your database with::

    $ python manage.py syncdb

Visit the URL ``/music/upload`` to upload your first track.

Features
~~~~~~~~

Upload
______


* View function: ``upload_track``
* Default URL: <app_mount_point>/upload

This wiew allows authenticated users to upload an audio file to the app.
Metadata is extracted from the file and used to prefill track attributes. Users
get redirected to the edit view.

Edit
____

* View function: ``edit_track``
* Default URL: <app_mount_point>/edit

Allow users to edit track attributes such as title, artist name, etc., upload an
image to attach to the track or replace the audio file itself. Modified metadata
are stored back in the audio file itself.

Display
_______

* View function: ``track_detail``
* URL: <app_mount_point_with_username>/track/<slug>

Display track. The URL pattern should captures a ``username`` argument, it will
be used in the query to select the track. For example, if the app is mounted
using the pattern ``"^(?P<username>[\w\._-]+)/music"``, a URL such as
/bob/music/track/love-forever will look for the track which slug is love-forever
and has been uploaded by bob. Without a username it will just use the slug to
find the track. A user who is logged in and owns the track can see links to the
edit page for this track. The default template uses the HTML5 audio element to
embed the track on the page. 

Delete
______

* View function: ``confirm_delete`` 
* Default URL: <app_mount_point>/confirm_delete/<id>

This is a confirmation page before deletion. Link to this page if you want to
provide a link to delete a track.

* View function: ``delete_track`` 
* Default URL: <app_mount_point>/delete

This view takes a track id as a POST parameter and delete the corresponding track.

User tracks listing
___________________

* View function: ``user_index``
* Default URL: <app_mount_point_with_username>/

If the app is mounted with a pattern containing a username such as
``"^(?P<username>[\w\._-]+)/music"``, a URL such as /bob/music will display a
list of tracks uploaded by bob.

Latest tracks listing
_____________________

* View function: ``latest_tracks``
* Default URL: <app_mount_point>/

Show latest tracks by all users.


.. _`Django`: http://djangoproject.com
.. _`mutagen`: http://code.google.com/p/mutagen/
.. _`ROOT_URLCONF`: http://docs.djangoproject.com/en/dev/ref/settings/#std:setting-ROOT_URLCONF
