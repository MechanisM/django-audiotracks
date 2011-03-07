from django.core.context_processors import request

from audiotracks.models import multiuser_mode


def multiuser_mode_processor(request):
    return {'multiuser_mode': multiuser_mode()}
