import os
from django.utils.translation import gettext_lazy as _
from .utils import ABS_PATH

TIME_ZONE = "UTC"

DEBUG = bool(os.getenv("DEBUG"))

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

USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

MEDIA_ROOT = ABS_PATH("media")
MEDIA_URL = "/media/"

STATIC_ROOT = ABS_PATH("../static")
STATIC_URL = "/static/"

STATICFILES_DIRS = ()

# Allow OSM tile servers to receive a Referer header (required by OSM tile policy).
# Django's SecurityMiddleware defaults to "same-origin", which strips the Referer
# on cross-origin requests, causing OSM tiles to return 403 "Access blocked".
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
<<<<<<< HEAD

# Allow OSM tile servers to receive a Referer header (required by OSM tile policy).
# Django's SecurityMiddleware defaults to "same-origin", which strips the Referer
# on cross-origin requests, causing OSM tiles to return 403 "Access blocked".
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
=======
>>>>>>> 3573fa9567027ccca045748a5241d2b977b6e578

# Allow OSM tile servers to receive a Referer header (required by OSM tile policy).
# Django's SecurityMiddleware defaults to "same-origin", which strips the Referer
# on cross-origin requests, causing OSM tiles to return 403 "Access blocked".
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"


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

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

AUTHENTICATION_BACKENDS = (
    "social_core.backends.openstreetmap_oauth2.OpenStreetMapOAuth2",
    "oauth2_provider.backends.OAuth2Backend",
    "social_core.backends.email.EmailAuth",
    "social_core.backends.username.UsernameAuth",
    "django.contrib.auth.backends.ModelBackend",
)
