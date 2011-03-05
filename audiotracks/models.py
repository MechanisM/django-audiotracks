import os

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from thumbs import ImageWithThumbsField

def multiuser_mode():
    return getattr(settings, 'AUDIOTRACKS_MULTIUSER', False)

def slugify_uniquely(value, obj, slugfield="slug"): 
    suffix = 1
    potential = base = slugify(value)
    filter_params = {}
    if multiuser_mode():
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


class Track(models.Model):
    user = models.ForeignKey(User,
        related_name = "tracks",
        blank = True,
        null = True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    audio_file = models.FileField(upload_to="audiotracks/audio_files")
    image = ImageWithThumbsField(upload_to="audiotracks/images", null=True,
            blank=True, sizes=((48,48), (200,200)))
    title = models.CharField(max_length="200", null=True)
    artist = models.CharField(max_length="200", null=True, blank=True)
    genre = models.CharField(max_length="200", null=True, blank=True)
    date = models.CharField(max_length="200", null=True, blank=True)
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

