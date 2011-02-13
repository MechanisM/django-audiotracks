import os

HERE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(HERE_DIR, "site_media")

DATABASE_ENGINE = 'sqlite3'
ROOT_URLCONF = ''
SITE_ID = 1
INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "audiotracks",

)

