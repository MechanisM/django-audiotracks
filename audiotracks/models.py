from django.db import models
from django.contrib.auth.models import User
from thumbs import ImageWithThumbsField

# Create your models here.

class Track(models.Model):
    user = models.ForeignKey(User,
        related_name = "tracks",
        blank = True,
        null = True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    audiofile = models.FileField(upload_to="audiotracks/audiofile")
    imagefile = ImageWithThumbsField(upload_to="audiotracks/imagefile", null=True,
            blank=True, sizes=((48,48), (200,200)))
    title = models.CharField(max_length="200", null=True)
    artist = models.CharField(max_length="200", null=True, blank=True)
    genre = models.CharField(max_length="200", null=True, blank=True)
    date = models.CharField(max_length="200", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
