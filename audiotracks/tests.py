import os
from os.path import dirname, abspath
import shutil

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
import mutagen

from audiotracks.models import Track

TEST_DATA_DIR = os.path.join(dirname(dirname(abspath(__file__))), 'tests', 'data')


class TestViews(TestCase):

    urls = 'urls'

    def setUp(self):
        User.objects.create_user("bob", "bob@example.com", "secret")
        User.objects.create_user("alice", "alice@example.com", "secret")
        self.client = Client()
        response = self.client.login(username='bob', password='secret')

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def get_upload_file(self, ext):
        filename = "audio_file." + ext
        filepath = os.path.join(TEST_DATA_DIR, filename)
        filehandle = open(filepath)
        return filename, filehandle

    def do_upload(self, ext):
        filename, filehandle = self.get_upload_file(ext)
        resp = self.client.post('/music/upload', {
            'name': filename,
            'audio_file': filehandle
            })

    def do_upload_as_user(self, username):
        response = self.client.logout()
        response = self.client.login(username=username, password='secret')
        self.do_upload('ogg')
        self.assert_(os.path.exists(os.path.join(settings.MEDIA_ROOT,
            "audiotracks", "audio_files", username, "audio_file.ogg")), 
            "Upload path should contain username")

    def verify_upload(self):
        track = Track.objects.get(genre="Test Data")
        self.assertEquals(track.title, "django-audiotracks test file")
        self.assertEquals(track.slug, "django-audiotracks-test-file")
        return track

    def do_edit(self, track, **params):
        default_params = {
            'title': 'New Title',
            'genre': 'New Genre',
            }
        default_params.update(params)
        return self.client.post('/music/edit/%s' % track.id,
                default_params)

    def test_upload_ogg(self):
        "OGG file upload"
        self.do_upload('ogg')
        track = self.verify_upload()
        self.assertEquals(track.mimetype, "audio/ogg")

    def test_upload_flac(self):
        "Flac file upload"
        self.do_upload('flac')
        track = self.verify_upload()
        self.assertEquals(track.mimetype, "audio/flac")

    def test_upload_mp3(self):
        "MP3 file upload"
        self.do_upload('mp3')
        track = self.verify_upload()
        self.assertEquals(track.mimetype, "audio/mpeg")

    def test_upload_wav(self):
        "WAV file upload"
        self.do_upload('wav')
        # WAV file metadata not currently supported
        track = Track.objects.get(id=1)
        assert 'wav' in track.audio_file.name
        self.assertEquals(track.slug, "audio_file")
        self.assertEquals(track.mimetype, "audio/x-wav")

    def test_edit_track_attributes(self, ext='ogg'):
        "Edit track attributes and verify that they get saved into the audiofile itself"
        self.do_upload(ext)
        track = Track.objects.get(genre="Test Data")
        self.do_edit(track, slug='new-title')
        track = Track.objects.get(genre="New Genre")
        self.assertEquals(track.title, 'New Title')
        audio_file_path = os.path.join(settings.MEDIA_ROOT,
            "audiotracks", "audio_files", "bob", "audio_file.%s" % ext)
        metadata = mutagen.File(audio_file_path, easy=True)
        self.assertEquals(metadata['title'], ['New Title'])
        self.assertEquals(metadata['genre'], ['New Genre'])

    def test_edit_mp3(self):
        "Edit MP3 track"
        self.test_edit_track_attributes('mp3')

    def test_edit_flac(self):
        "Edit FLAC track"
        self.test_edit_track_attributes('flac')

    def test_edit_wav(self):
        "Edit WAV track"
        ext = 'wav'
        self.do_upload(ext)
        track = Track.objects.get(slug="audio_file")
        self.do_edit(track, slug='new-title')
        track = Track.objects.get(genre="New Genre")
        self.assertEquals(track.title, 'New Title')

    def test_replace_track_file(self):
        "Update audio file for a track"

        # Upload mp3
        self.do_upload('mp3')

        # Update track with ogg file
        track_id = Track.objects.get(genre="Test Data").id
        filename, filehandle = self.get_upload_file('ogg')
        resp = self.client.post('/music/edit/%s' % track_id, {
            'name': filename,
            'audio_file': filehandle,
            'title': "New Title",
            'genre': "New Genre",
            'slug': "new-slug",
            })

        # Check that the file has been replaced
        track = Track.objects.get(id=track_id)
        self.assert_(track.audio_file.path.endswith('.ogg'))

    def test_delete_image(self):
        "Attach and remove track image"
        self.do_upload('ogg')
        track = Track.objects.get(genre="Test Data")
        self.do_edit(track, slug='new-title',
            image=open(os.path.join(TEST_DATA_DIR, 'image.jpg')))
        track = Track.objects.get(title="New Title")
        self.assert_(track.image.url.endswith('image.jpg'),
                "Image should have been added")
        self.do_edit(track, slug='new-title', delete_image='1')
        track = Track.objects.get(title="New Title")
        self.assertFalse(track.image, "Image should have been deleted")

    def test_confirm_delete_track(self):
        "Confirm delete track"
        self.do_upload('ogg')
        track = Track.objects.get(genre="Test Data")
        resp = self.client.get('/music/confirm_delete/%s' % track.id)
        assert 'Are you sure' in resp.content

    def test_delete_track(self):
        "Delete track"
        self.do_upload('ogg')
        track = Track.objects.get(genre="Test Data")
        resp = self.client.post('/music/delete', {'track_id': track.id,
            'came_from': '/somewhere'})
        self.assertEquals(Track.objects.count(), 0)

    def test_latest(self):
        "Get latest tracks"
        self.do_upload('ogg')
        resp = self.client.get('/bob/music')
        # Check that slug is in listing content
        assert 'django-audiotracks-test-file' in resp.content

    def test_get_track(self):
        "Get track"
        self.do_upload_as_user('bob')
        self.do_upload_as_user('alice')
        bob_track, alice_track = Track.objects.all()
        self.assertEquals(bob_track.user.username, 'bob')
        self.assertEquals(alice_track.user.username, 'alice')
        self.assertEquals(bob_track.slug, alice_track.slug)
        self.client.get('/bob/music/track/' + bob_track.slug)

    def test_prevent_duplicate_slug(self):
        "Prevent duplicate slug for the same user"
        # Upload a track
        self.do_upload('ogg')

        # Upload another one as another user
        self.do_upload_as_user('alice')
        bob_track, alice_track = Track.objects.all()
        self.assertEquals(bob_track.slug, alice_track.slug,
                "We should be able to create 2 tracks as 2 different users "
                "with the same slug.")

        # We should be allowed to set the same slug for 2 tracks belonging to 2
        # different users
        self.do_edit(alice_track, slug='django-audiotracks-test-file')
        _, alice_track  = Track.objects.all()
        self.assertEquals(alice_track.slug, 'django-audiotracks-test-file')
        
        # We should not be able to set the same slug for 2 tracks belonging to
        # the same user
        self.do_upload_as_user('alice')
        _, existing_alice_track, new_alice_track = Track.objects.all()
        self.do_edit(new_alice_track, slug='django-audiotracks-test-file')
        _, existing_alice_track, new_alice_track = Track.objects.all()
        self.assertEquals(new_alice_track.slug, 'django-audiotracks-test-file-2')
