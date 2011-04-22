import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from thumbs import ImageWithThumbsField
from tagging.fields import TagField

def slugify_uniquely(value, obj, slugfield="slug"): 
    suffix = 1
    potential = base = slugify(value)
    filter_params = {}
    filter_params['user'] = obj.user
    while True:
        if suffix > 1:
            potential = "-".join([base, str(suffix)])
        filter_params[slugfield] = potential
        obj_count = obj.__class__.objects.filter(**filter_params).count()
        if not obj_count:
            return potential
        # we hit a conflicting slug, so bump the suffix & try again
        suffix += 1


def get_upload_path(dirname, obj, filename):
    return os.path.join("audiotracks", dirname, obj.user.username, filename)

def get_images_upload_path(obj, filename):
    return get_upload_path("images", obj, filename)

def get_audio_upload_path(obj, filename):
    return get_upload_path("audio_files", obj, filename)


class Track(models.Model):
    user = models.ForeignKey(User,
        related_name = "tracks",
        blank = True,
        null = True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    audio_file = models.FileField(upload_to=get_audio_upload_path)
    image = ImageWithThumbsField(upload_to=get_images_upload_path, null=True,
            blank=True, sizes=((48,48), (200,200)))
    title = models.CharField(max_length="200", null=True)
    artist = models.CharField(max_length="200", null=True, blank=True)
    genre = models.CharField(max_length="200", null=True, blank=True)
    date = models.CharField(max_length="200", null=True, blank=True)
    tags = TagField()
    description = models.TextField(null=True, blank=True)
    slug = models.SlugField(verbose_name="Slug (last part of the url)")
    _original_slug = None # Used to detect slug change

    def __init__(self, *args, **kwargs):
        super(Track, self).__init__(*args, **kwargs)
        self._original_slug = self.slug

    def __unicode__(self):
        return "Track '%s' uploaded by '%s'" % (self.title, self.user.username)

    def save(self, **kwargs):
        if not self.slug:
            # Automatically set initial slug
            slug_source = getattr(self, 'title') or \
                    os.path.splitext(os.path.basename(self.audio_file.name))[0]
            self.slug = slugify_uniquely(slug_source, self)
        super(Track, self).save(**kwargs)


    @models.permalink
    def get_absolute_url(self):
        return ('audiotracks.views.track_detail', [self.user.username, self.slug])
