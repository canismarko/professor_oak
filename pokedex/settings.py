"""
Django settings for pokedex project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import mimetypes
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

#Add support for .svg and .svgz file rendering
mimetypes.add_type("image/svg+xml", ".svg", True)
mimetypes.add_type("image/svg+xml", ".svgz", True)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'x+$ouifu9a(ugp_(qml-44h7dwf(2unxykoi0()l7sqi#^^*!)'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django_browserid', # Mozilla persona authentication
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'easy_thumbnails', # from https://github.com/jonasundderwolf/django-image-cropping
	'image_cropping', # from https://github.com/jonasundderwolf/django-image-cropping
	'pokedex'
)

# Add the django_browserid authentication backend.
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_browserid.auth.BrowserIDBackend',
)

BROWSERID_CREATE_USER = False

LOGIN_REDIRECT_URL_FAILURE = '/unauthorized/'

LOGIN_REDIRECT_URL = '/'

REDIRECT_UNAUTHORIZED_USER = '../../../unauthorized/'

#User image-cropping configuration
from easy_thumbnails.conf import Settings as thumbnail_settings
THUMBNAIL_PROCESSORS = (
	'image_cropping.thumbnail_processors.crop_corners',
	) + thumbnail_settings.THUMBNAIL_PROCESSORS

#Had to extract the /static/image_cropping to my static folder from the master zip before this would work for some reason


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'pokedex.urls'

WSGI_APPLICATION = 'pokedex.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_ROOT = 'static_files/'
STATIC_URL = '/static/'

MEDIA_ROOT = '.'
MEDIA_URL = '/media/'
