import os
from os.path import dirname, abspath

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from audiotracks.models import Track


class TestViews(TestCase):

    urls = 'test_urls'

    def setUp(self):
        User.objects.create_user("bob", "bob@example.com", "secret")
        self.client = Client()
        response = self.client.login(username='bob', password='secret')

    def do_upload(self, ext):
        filename = "audio_file." + ext
        filepath = os.path.join(dirname(dirname(abspath(__file__))), 'tests', 
                'data', filename)
        filehandle = open(filepath)
        resp = self.client.post('/bob/music/upload_track', {
            'name': filename,
            'audio_file': filehandle
            })

    def verify_upload(self):
        track = Track.objects.get(genre="Test Data")
        self.assertEquals(track.title, "django-audiotracks test file")
        self.assertEquals(track.slug, "django-audiotracks-test-file")

    def test_upload_ogg(self):
        self.do_upload('ogg')
        self.verify_upload()

    def test_upload_flac(self):
        self.do_upload('flac')
        self.verify_upload()

    def test_upload_mp3(self):
        self.do_upload('mp3')
        self.verify_upload()

    def test_upload_wav(self):
        self.do_upload('wav')
        # WAV file metadata not currently supported
        track = Track.objects.get(id=1)
        assert 'wav' in track.audio_file.name
        self.assertEquals(track.slug, "audio_filewav")

    def test_detail(self):
        self.do_upload('ogg')
        resp = self.client.get('/al/music/track/django-audiotracks-test-file')
        assert 'Alex' in resp.content
        assert 'Test Data' in resp.content

    def test_latest(self):
        self.do_upload('ogg')
        resp = self.client.get('/al/music')
        # Check that slug is in listing content
        assert 'django-audiotracks-test-file' in resp.content

    def test_confirm_delete_track(self):
        self.do_upload('ogg')
        track = Track.objects.get(genre="Test Data")
        resp = self.client.get('/al/music/confirm_delete_track/%s' % track.id)
        assert 'Are you sure' in resp.content

    def test_delete_track(self):
        self.do_upload('ogg')
        track = Track.objects.get(genre="Test Data")
        resp = self.client.post('/al/music/delete_track', {'track_id': track.id,
            'came_from': '/somewhere'})
        self.assertEquals(Track.objects.count(), 0)

