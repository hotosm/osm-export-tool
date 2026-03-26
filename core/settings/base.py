# -*- coding: utf-8 -*-
from __future__ import absolute_import

import os
from django.utils.translation import gettext_lazy as _
from .utils import ABS_PATH

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = "UTC"

# default DEBUG setting
# Set debug to true for development
DEBUG = bool(os.getenv("DEBUG"))

# from django.utils.crypto import get_random_string
# secret_key = get_random_string(50, 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)')
AUTH_PROVIDER = os.getenv("AUTH_PROVIDER", "legacy")

# Hanko SSO Configuration
if AUTH_PROVIDER == "hanko":
    HANKO_API_URL = os.getenv("HANKO_API_URL")
    HANKO_PUBLIC_URL = os.getenv("HANKO_PUBLIC_URL", HANKO_API_URL)
    COOKIE_SECRET = os.getenv("COOKIE_SECRET")
    COOKIE_DOMAIN = os.getenv("COOKIE_DOMAIN", None)
    COOKIE_SECURE = not DEBUG if os.getenv("COOKIE_SECURE") is None else os.getenv("COOKIE_SECURE", "").lower() in ("true", "1", "yes")

if "SECRET_KEY" not in os.environ:
    print("WARNING: secret key not set - setting a default for development.")
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en"

LANGUAGES = (
    ("en", _("English")),
    ("id", _("Bahasa Indonesia")),
    ("de", _("German")),
    ("es", _("Spanish")),
    ("ja", _("Japanese")),
    ("fr", _("French")),
)

LOCALE_PATHS = (ABS_PATH("locales"),)

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ABS_PATH("media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = "/media/"

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ABS_PATH("../static")

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = "/static/"

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # ABS_PATH('core', 'base_static'),
)

# Allow OSM tile servers to receive a Referer header (required by OSM tile policy).
# Django's SecurityMiddleware defaults to "same-origin", which strips the Referer
# on cross-origin requests, causing OSM tiles to return 403 "Access blocked".
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


# default middleware classes
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "oauth2_provider.middleware.OAuth2TokenMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "social_django.middleware.SocialAuthExceptionMiddleware",
]

if AUTH_PROVIDER == "hanko":
    auth_middleware_index = MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware")
    MIDDLEWARE.insert(auth_middleware_index, "hotosm_auth_django.HankoAuthMiddleware")

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.hotosm\.test$",
    r"^https://.*\.hotosm\.org$",
    r"^http://localhost(:\d+)?$",
    r"^http://127\.0\.0\.1(:\d+)?$",
]

# Python dotted path to the WSGI application used by Django's runserver.
ROOT_URLCONF = "core.urls"
WSGI_APPLICATION = "core.wsgi.application"

INSTALLED_APPS = [
    "django.contrib.admin.apps.SimpleAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django.contrib.postgres",
    "raven.contrib.django.raven_compat",
    "oauth2_provider",
    "corsheaders",
]

if AUTH_PROVIDER == "hanko":
    INSTALLED_APPS.append("hotosm_auth_django")

# enable cached storage
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

AUTHENTICATION_BACKENDS = (
    # "social_core.backends.openstreetmap.OpenStreetMapOAuth",
    "social_core.backends.openstreetmap_oauth2.OpenStreetMapOAuth2",
    "oauth2_provider.backends.OAuth2Backend",
    "social_core.backends.email.EmailAuth",
    "social_core.backends.username.UsernameAuth",
    "django.contrib.auth.backends.ModelBackend",
)
