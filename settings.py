import os.path
# Django settings for drinkkit project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('You', 'you@you.com'),
)

FIXTURE_DIRS = (
	'fixtures',
)

if DEBUG:
	CACHE_BACKEND = 'dummy:///'
else:
	CACHE_BACKEND = 'memcached://127.0.0.1:11211/'

AUTH_PROFILE_MODULE = 'redditors.Redditor'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/auth/'
LOGOUT_URL = '/'

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'America/New_York'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = '-2_vd&w^n^3l2+jg3bxrqv8$7w4%lolnok(hf_dl5-()a=3xl5'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.cache.FetchFromCacheMiddleware',
)

ROOT_URLCONF = 'drinkkit.urls'

TEMPLATE_DIRS = (
	os.path.join(os.path.dirname(__file__), 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
	'django.contrib.gis',
	'django.contrib.admin',
	'redditors',
)
