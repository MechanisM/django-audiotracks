import os
import tempfile

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.core.files.uploadhandler import TemporaryFileUploadHandler
from django.core import urlresolvers 
from django import forms
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
import mutagen

from audiotracks.models import Track


class TrackUploadForm(forms.ModelForm):
    class Meta:
        model = Track
        fields = ('audio_file',)

class TrackEditForm(forms.ModelForm):
    class Meta:
        model = Track
        exclude = ('user', 'created_at', 'updated_at')

def index(request, username):
    tracks = Track.objects.all()
    return render_to_response("audiotracks/latest.html", {'username': username, 
        'tracks': tracks}, context_instance=RequestContext(request))

def user_index(request, username):
    tracks = request.user.tracks.all()
    return render_to_response("audiotracks/user_index.html", {'username': username, 
        'tracks': tracks}, context_instance=RequestContext(request))

def track_detail(request, username, track_slug):
    track = Track.objects.get(slug=track_slug)
    return render_to_response("audiotracks/detail.html", {'username': username, 'track': track}, 
            context_instance=RequestContext(request))

@login_required
@csrf_exempt # request.POST is accessed by CsrfViewMiddleware
def upload_track(request, username):
    request.upload_handlers = [TemporaryFileUploadHandler()] # before accessing POST
    if request.method == "POST":
        form = TrackUploadForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = request.FILES['audio_file']
            audio_file_path = audio_file.temporary_file_path()
            metadata = mutagen.File(audio_file_path, easy=True)
            track = form.save(commit=False)
            track.user = request.user
            for field in ('title', 'artist', 'genre', 'description', 'date'):
                if metadata and metadata.get(field):
                    setattr(track, field, metadata.get(field)[0])
            track.save()
            return HttpResponseRedirect(urlresolvers.reverse('edit_track',
                args=[username, track.id]))
    else:
        form = TrackUploadForm()
    return render_to_response("audiotracks/new.html", {'form':form},
            context_instance=RequestContext(request))

@login_required
def edit_track(request, username, track_id):
    track = request.user.tracks.get(id=track_id)
    if request.method == "POST":
        form = TrackEditForm(request.POST, request.FILES, instance=track)
        if form.is_valid():
            track = form.save()
            if 'delete_image' in request.POST:
                track.image = None
                track.save()
            messages.add_message(request, messages.INFO, 'Your changes have been saved.')
            return HttpResponseRedirect(urlresolvers.reverse('user_index',
                args=[username]))
    else:
        form = TrackEditForm(instance=track, )
    track_url_prefix = request.build_absolute_uri(urlresolvers.reverse('track_detail',
        args=[username, '']))
    track_filename = os.path.basename(track.audio_file.name)
    return render_to_response("audiotracks/edit.html", {
        'form': form,
        'track': track, 
        'track_url_prefix': track_url_prefix,
        'track_filename': track_filename,
        }, context_instance=RequestContext(request))

@login_required
def confirm_delete_track(request, username, track_id):
    track = request.user.tracks.get(id=track_id)
    return render_to_response("audiotracks/confirm_delete.html", {
        'track': track,
        'came_from': request.GET.get('came_from', 
            urlresolvers.reverse('user_index', args=[username]))
        }, context_instance=RequestContext(request))

@login_required
def delete_track(request, username):
    track_id = request.POST.get('track_id')
    track = request.user.tracks.get(id=track_id)
    track.delete()
    messages.add_message(request, messages.INFO, '"%s" has been deleted.' % track.title)
    return HttpResponseRedirect(request.POST.get('came_from', '/'))
