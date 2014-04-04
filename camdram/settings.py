"""
Django settings for camdram project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = '/srv/http/static/'
MEDIA_ROOT = '/srv/http/'
MEDIA_URL = '/'
LOGIN_URL = '/auth/login'
LOGIN_REDIRECT_URL = '/'
TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
    )


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'c^g6z6@^f&6@0v$n(4_r*s36eea3nkn-sq_(swkmmnn2(tdzm7'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['.camdram.net']


# Application definition

INSTALLED_APPS = (
#    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',
    'registration',
    'guardian',
    'haystack',
    'south',
    'autocomplete_light',
    'pipeline',
    'drama',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'camdram.urls'

WSGI_APPLICATION = 'camdram.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', 
        'NAME': 'camdram',
        'USER': 'camdram',
        'PASSWORD': 'hello, little girl',
        'HOST': '',   # Or an IP Address that your DB is hosted on
        'PORT': '',
        #'ENGINE': 'django.db.backends.sqlite3',
        #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

TEMPLATE_CONTEXT_PROCESSORS = ("django.contrib.auth.context_processors.auth",
                               "django.core.context_processors.debug",
                               "django.core.context_processors.i18n",
                               "django.core.context_processors.media",
                               "django.core.context_processors.static",
                               "django.core.context_processors.tz",
                               "django.contrib.messages.context_processors.messages",
                               "drama.processors.navitems_processor",
                               "drama.processors.searchform",
                               )

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'camdram',
    },
}

HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # this is default
    'drama.auth.EmailBackend',
    'guardian.backends.ObjectPermissionBackend',
    )

ANONYMOUS_USER_ID = -1

GUARDIAN_RAISE_403 = True

STATICFILES_STORAGE = 'pipeline.storage.PipelineCachedStorage'

PIPELINE_CSS = {
    'vendor': {
        'source_filenames': (
            'stylesheets/font-awesome/css/font-awesome.css',
            'stylesheets/jquery-ui/minified/jquery-ui.min.css',
            'stylesheets/h5bp/*.css',
            'stylesheets/foundation/*.css',
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

PIPELINE_JS = {
    'vendor': {
        'source_filenames': (
            'javascripts/jquery/jquery-1.11.0.min.js',
            'javascripts/jquery-ui/jquery-ui.min.js',
            'javascripts/foundation/foundation/foundation.js',
            'javascripts/foundation/foundation/foundation.*.js',
            'javascripts/foundation/vendor/custom.modernizr.js',
        ),
        'output_filename': 'js/vendor.js',
    },
    'app': {
        'source_filenames': (
            'javascripts/camdram/autocomplete.js',
        ),
        'output_filename': 'js/app.js'
    },
}

PIPELINE_DISABLE_WRAPPER = True

