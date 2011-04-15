import os
from os.path import dirname, abspath
import shutil

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from audiotracks.models import Track

TEST_DATA_DIR = os.path.join(dirname(dirname(abspath(__file__))), 'tests', 'data')


class TestViewsMixin(object):
    """
    Mixin class which contains methods used by both single user mode and multi
    user mode.
    """

    def setUp(self):
        User.objects.create_user("bob", "bob@example.com", "secret")
        User.objects.create_user("alice", "alice@example.com", "secret")
        self.client = Client()
        response = self.client.login(username='bob', password='secret')

    def tearDown(self):
        if os.path.exists(settings.MEDIA_ROOT):
            shutil.rmtree(settings.MEDIA_ROOT)

    def do_upload(self, ext):
        filename = "audio_file." + ext
        filepath = os.path.join(TEST_DATA_DIR, filename)
        filehandle = open(filepath)
        resp = self.client.post('/music/upload', {
            'name': filename,
            'audio_file': filehandle
            })

    def do_upload_as_user(self, username):
        response = self.client.logout()
        response = self.client.login(username=username, password='secret')
        self.do_upload('ogg')
        if settings.AUDIOTRACKS_MULTIUSER:
            self.assert_(os.path.exists(os.path.join(settings.MEDIA_ROOT,
                "audiotracks", "audio_files", username, "audio_file.ogg")), 
                "Upload path should contain username")
        else:
            self.assert_(os.path.exists(os.path.join(settings.MEDIA_ROOT,
                "audiotracks", "audio_files", "audio_file.ogg")), 
                "Upload path should not contain username")

    def verify_upload(self):
        track = Track.objects.get(genre="Test Data")
        self.assertEquals(track.title, "django-audiotracks test file")
        self.assertEquals(track.slug, "django-audiotracks-test-file")

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
        self.verify_upload()

    def test_upload_flac(self):
        "Flac file upload"
        self.do_upload('flac')
        self.verify_upload()

    def test_upload_mp3(self):
        "MP3 file upload"
        self.do_upload('mp3')
        self.verify_upload()

    def test_upload_wav(self):
        "WAV file upload"
        self.do_upload('wav')
        # WAV file metadata not currently supported
        track = Track.objects.get(id=1)
        assert 'wav' in track.audio_file.name
        self.assertEquals(track.slug, "audio_file")

    def test_edit(self):
        "Edit track"
        self.do_upload('ogg')
        track = Track.objects.get(genre="Test Data")
        self.do_edit(track, slug='new-title')
        track = Track.objects.get(genre="New Genre")
        self.assertEquals(track.title, 'New Title')


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


class TestSingleUser(TestViewsMixin, TestCase):

    urls = 'single_user_urls'

    def setUp(self):
        settings.AUDIOTRACKS_MULTIUSER = False
        super(TestSingleUser, self).setUp()

    def test_latest(self):
        "Get latest tracks"
        self.do_upload('ogg')
        resp = self.client.get('/music')
        # Check that slug is in listing content
        assert 'django-audiotracks-test-file' in resp.content

    def test_get_track(self):
        "Get track in single user mode"
        self.do_upload('ogg')
        resp = self.client.get('/music/track/django-audiotracks-test-file')

    def test_prevent_duplicate_slug(self):
        "In single user mode, prevent duplicate slug accross the whole database"
        # Upload a track
        self.do_upload('ogg')

        # Upload another one as another user
        self.do_upload_as_user('alice')
        bob_track, alice_track = Track.objects.all()

        # We should not be allowed to set the same slug for both tracks
        self.do_edit(alice_track, slug='django-audiotracks-test-file')
        bob_track, alice_track = Track.objects.all()
        self.assertEquals(alice_track.slug, 'django-audiotracks-test-file-2',
                'We should not be allowed to set the same slug for both tracks')

        # However we should be allowed to set a different slug for that new track
        self.do_edit(alice_track, slug='new-slug')
        tracks = Track.objects.all()
        alice_track = Track.objects.get(id=alice_track.id) # Reload from db
        self.assertEquals(alice_track.slug, 'new-slug')


class TestMultiUser(TestViewsMixin, TestCase):

    urls = 'multi_user_urls'

    def setUp(self):
        settings.AUDIOTRACKS_MULTIUSER = True
        super(TestMultiUser, self).setUp()

    def test_latest(self):
        "Get latest tracks"
        self.do_upload('ogg')
        resp = self.client.get('/al/music')
        # Check that slug is in listing content
        assert 'django-audiotracks-test-file' in resp.content

    def test_get_track(self):
        "Get track in multiuser mode"
        self.do_upload_as_user('bob')
        self.do_upload_as_user('alice')
        bob_track, alice_track = Track.objects.all()
        self.assertEquals(bob_track.user.username, 'bob')
        self.assertEquals(alice_track.user.username, 'alice')
        self.assertEquals(bob_track.slug, alice_track.slug)
        self.client.get('/bob/music/track/' + bob_track.slug)

    def test_prevent_duplicate_slug(self):
        "In multi-user mode, prevent duplicate slug for the same user"
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


