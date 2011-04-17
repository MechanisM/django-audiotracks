==================
django-audiotracks
==================

A Django_ app to publish audio tracks.

Introduction
~~~~~~~~~~~~

django-audiotracks is a basic reusable Django_ application that allows users to
publish audio tracks. It's tested with Ogg Vorbis, Flac, MP3 and WAV files. It
provides a Track model, a set of views, default templates and sensible default
URL configuration.  It uses mutagen_ to extract metadata from the audio files
and prefill track attributes.  PIL is also required to process the image that
can be attached to a track.  


Installation
~~~~~~~~~~~~

Install the ``audiotracks`` package in your Python path. A ``setup.py`` script is provided. You
can use it with a command such as::

    $ python setup.py develop

Run the example project
~~~~~~~~~~~~~~~~~~~~~~~

A minimal sample project is provided with the source code::

    $ cd <django-audiotracks source dir>/example_project/
    $ python manage.py syncdb      # Create initial user at this stage
    $ python manage.py runserver

Log in and start uploading tracks.


Add ``audiotracks`` to your app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Edit ``settings.py`` and add ``audiotracks`` to your list of
``INSTALLED_APPS``. Then synchronize your database with::

    $ python manage.py syncdb

Edit your ROOT_URLCONF_ and add a piece of code similar to::

    urlpatterns += patterns('',
        # Here we mount the app under /music. Feel free to use something else
        url("^music", include("audiotracks.urls")),
        # Some URLs require a Django username
        url("^(?P<username>[\w\._-]+)/music", include("audiotracks.urls")),
    )

Visit the URL ``/music/upload`` to upload your first track.

Features
~~~~~~~~

Upload
______


* View function: ``upload_track``
* Default URL: <app_mount_point>/upload

This view allows authenticated users to upload an audio file.
Metadata is extracted from the file and used to prefill track attributes. Users
get redirected to the edit view.

Edit
____

* View function: ``edit_track``
* Default URL: <app_mount_point>/edit/<id>

Allow users to edit track attributes such as title, artist name, etc., upload an
image to attach to the track or replace the audio file itself. Modified metadata
is stored back into the audio file itself if the format supports it, eg. it won't
work with a WAV file.

Display
_______

* View function: ``track_detail``
* URL: <app_mount_point_containing_username>/track/<slug>

Display track. The URL pattern must capture a ``username`` argument, it will be
used in the query to select the track. For example, if the app is mounted using
the pattern ``"^(?P<username>[\w\._-]+)/music"``, a URL such as
/bob/music/track/love-forever will look for the track which slug is love-forever
and has been uploaded by bob. A user who is logged in and owns the track can see
links to the edit page for this track. The default template uses the HTML5 audio
element to embed the track on the page. 

Delete
______

* View function: ``confirm_delete`` 
* Default URL: <app_mount_point>/confirm_delete/<id>

This is a confirmation page before deletion. Link to this page if you want to
provide a link to delete a track.

* View function: ``delete_track`` 
* Default URL: <app_mount_point>/delete (takes id as POST a param)

This view takes a track id as a POST parameter and delete the corresponding track.

User tracks listing
___________________

* View function: ``user_index``
* Default URL: <app_mount_point_containing_username>/

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
