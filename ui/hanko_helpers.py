import logging
from functools import wraps
from typing import Optional
from django.conf import settings
from django.contrib.auth.decorators import login_required as django_login_required
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication

LOG = logging.getLogger(__name__)

APP_NAME = "osm-export-tool"


def login_required(view_func):
    """Require an authenticated user under either auth provider.

    hotosm_auth_django's decorator checks request.hanko_user, which only exists
    when HankoAuthMiddleware is installed — under AUTH_PROVIDER=legacy it is
    never set, so every decorated view would answer 401 regardless of the
    session. Fall back to Django's decorator there, keeping the redirect to
    LOGIN_URL these views have always returned.

    The provider is read per request so tests can flip it with override_settings.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if getattr(settings, "AUTH_PROVIDER", "legacy") == "hanko":
            from hotosm_auth_django import login_required as hanko_login_required

            return hanko_login_required(view_func)(request, *args, **kwargs)
        return django_login_required(view_func)(request, *args, **kwargs)

    return wrapper


class HankoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        if not hasattr(request, 'hotosm') or not request._request.hotosm.user:
            return None

        # no auto-creation — onboarding flow handles user/mapping creation
        hanko_user = request._request.hotosm.user
        django_user = get_mapped_django_user_by_hanko(hanko_user)

        if django_user:
            return (django_user, None)

        return None


def get_mapped_django_user_by_hanko(hanko_user) -> Optional[User]:
    from hotosm_auth_django import get_mapped_user_id

    mapped_user_id = get_mapped_user_id(hanko_user, app_name=APP_NAME)
    if mapped_user_id:
        try:
            user = User.objects.get(pk=int(mapped_user_id))
            LOG.debug(f"Found mapped user: hanko={hanko_user.id} -> django={user.pk}")
            return user
        except (User.DoesNotExist, ValueError):
            LOG.warning(f"Mapping exists but user not found: {mapped_user_id}")

    return None


# Both names mean "this Django user is connected to this OSM account", and the
# uid is the OSM user id either way. `openstreetmap` is the OAuth1-era provider;
# `openstreetmap-oauth2` is what the current login writes. Production carries
# 55k accounts under the old name and 43k under the new one, so matching only
# the new one leaves 55% of users to the email fallback.
OSM_SOCIAL_AUTH_PROVIDERS = ("openstreetmap-oauth2", "openstreetmap")


def find_legacy_user_by_osm_id(osm_id: int) -> Optional[User]:
    """Return the Django user connected to this OSM account, or None.

    A uid can appear under both providers, and 630 uids in production point at
    two different users (duplicate accounts for one OSM identity), so the pick
    has to be deterministic rather than blowing up on MultipleObjectsReturned:
    prefer the modern provider, then the oldest account.
    """
    from django.db.models import Case, IntegerField, When
    from social_django.models import UserSocialAuth

    social_auth = (
        UserSocialAuth.objects.filter(
            provider__in=OSM_SOCIAL_AUTH_PROVIDERS,
            uid=str(osm_id),
        )
        .order_by(
            Case(
                When(provider="openstreetmap-oauth2", then=0),
                default=1,
                output_field=IntegerField(),
            ),
            "user_id",
        )
        .first()
    )

    return social_auth.user if social_auth else None


def find_legacy_user_by_email(email: str) -> Optional[User]:
    if not email:
        return None
    return User.objects.filter(email=email).order_by('id').first()


def create_export_tool_user(
    username: str,
    email: Optional[str] = None,
) -> User:
    final_username = username
    suffix = 1
    while User.objects.filter(username=final_username).exists():
        final_username = f"{username}_{suffix}"
        suffix += 1

    user = User.objects.create_user(
        username=final_username,
        email=email or "",
    )

    LOG.info(f"Created User: id={user.id}, username={final_username}")
    return user


def get_mapped_django_user(request) -> Optional[User]:
    if not is_hanko_authenticated(request):
        return None

    hanko_user = request.hotosm.user
    return get_mapped_django_user_by_hanko(hanko_user)


def is_hanko_authenticated(request):
    return hasattr(request, 'hotosm') and request.hotosm.user is not None


def is_hanko_admin(email):
    """Return True if the given email is in the ADMIN_EMAILS setting."""
    admin_emails = [
        e.strip()
        for e in getattr(settings, 'ADMIN_EMAILS', '').split(',')
        if e.strip()
    ]
    return email in admin_emails
