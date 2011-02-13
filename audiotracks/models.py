from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from thumbs import ImageWithThumbsField

def slugify_uniquely(value, model, slugfield="slug"): 
    """Returns a slug on a name which is unique within a model's table

    This code suffers a race condition between when a unique
    slug is determined and when the object with that slug is saved.
    It's also not exactly database friendly if there is a high
    likelyhood of common slugs being attempted.

    A good usage pattern for this code would be to add a custom save()
    method to a model with a slug field along the lines of:

            from django.template.defaultfilters import slugify

            def save(self):
                if not self.id:
                    # replace self.name with your prepopulate_from field
                    self.slug = slugify_uniquely(self.name, self.__class__)
            super(ClassName, self).save()
    
    Copied from http://code.djangoproject.com/wiki/slugify_uniquely
    Original pattern discussed at
    http://www.b-list.org/weblog/2006/11/02/django-tips-auto-populated-fields
    """
    suffix = 0
    potential = base = slugify(value)
    while True:
            if suffix:
                    potential = "-".join([base, str(suffix)])
            if not model.objects.filter(**{slugfield: potential}).count():
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

    def save(self, **kwargs):
        if hasattr(self, 'title') and self.title:
            self.slug = slugify_uniquely(self.title, self.__class__)
        else:
            self.slug = slugify_uniquely(self.audio_file.name, self.__class__)
        super(Track, self).save(**kwargs)
