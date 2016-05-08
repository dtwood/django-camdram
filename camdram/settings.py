"""
Django settings for camdram project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from celery.schedules import crontab
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/'
LOGIN_URL = '/auth/login'
LOGIN_REDIRECT_URL = '/'

EMAIL_FROM_DOMAIN = 'camdram.com'
NEW_ISSUE_ADDRESSES = ['websuport']
DOMAIN_FOR_URI = 'http://www.camdram.com'


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c^g6z6@^f&6@0v$n(4_r*s36eea3nkn-sq_(swkmmnn2(tdzm7'
FACEBOOK_ACCESS_TOKEN = '442245022574342|56555ade12f03b8a1474c50ce8b5a66c'
TWITTER_KEY = 'nfZQqlLtFQQN8ak04uVqwE4WU'
TWITTER_SECRET = 'm6ogFwuxBKQCaBYOKVafuvrStGhIJgJwm6vVP1LgYpj4lcLZAS'


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['.camdram.net']

INTERNAL_IPS = ('127.0.0.1',)

# Application definition

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ os.path.join(BASE_DIR, 'templates') ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors':  [
                "django.contrib.auth.context_processors.auth",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.core.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "drama.processors.navitems_processor",
                "drama.processors.searchform",
            ],
        },
    },
]

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'registration',
    'guardian',
    'haystack',
    'dal',
    'pipeline',
    'rest_framework',
    'drama',
    'grappelli',
    'django.contrib.admin',
    'issues',
    'autofixture',
    'django_extensions',
    'reversion',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'reversion.middleware.RevisionMiddleware',
)

ROOT_URLCONF = 'camdram.urls'

WSGI_APPLICATION = 'camdram.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        #'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        #'NAME': 'camdram',
        #'USER': 'camdram',
        #'PASSWORD': 'four bears, four bears',
        #'HOST': '',   # Or an IP Address that your DB is hosted on
        #'PORT': '',
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, 'emails')

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index'),
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'drama.auth.EmailBackend',
    'drama.auth.RulePermissionsBackend',
    'guardian.backends.ObjectPermissionBackend',
    )

ANONYMOUS_USER_ID = -1

GUARDIAN_RAISE_403 = True

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE = {}
PIPELINE['STYLESHEETS'] = {
    'vendor': {
        'source_filenames': (
            'stylesheets/h5bp/*.css',
            'stylesheets/lightbox/*.css',
        ),
        'output_filename': 'css/vendor.css',
    },
    'app': {
        'source_filenames': (
            'stylesheets/camdram/*.css',
        ),
        'output_filename': 'css/main.css'
    },
}

PIPELINE['CSS_COMPRESSOR'] = 'pipeline.compressors.NoopCompressor'
PIPELINE['JS_COMPRESSOR'] = 'pipeline.compressors.NoopCompressor'


PIPELINE_ENABLED = True

PIPELINE['JAVASCRIPT'] = {
    'vendor': {
        'source_filenames': (
            'javascripts/moment.js',
            'javascripts/lightbox/*.js',
        ),
        'output_filename': 'js/vendor.js',
    },
    'app': {
        'source_filenames': (
            'javascripts/camdram/*.js',
        ),
        'output_filename': 'js/app.js'
    },
    'diary': {
        'source_filenames': (
            'javascripts/camdram/diary.js',
            ),
        'output_filename':' js/diary.js'
    },
}

PIPELINE_DISABLE_WRAPPER = True

DRAMA_DIARY_ROW_HEIGHT = 30 #in minutes

ACCOUNT_ACTIVATION_DAYS = 7

CELERYBEAT_SCHEDULE = {
    'social-news-update': {
        'task':'camdram.update-posts',
        'schedule': crontab(minute='*/15'),
        }
    }
