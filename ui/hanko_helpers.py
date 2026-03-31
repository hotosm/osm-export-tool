import logging
from functools import wraps
from typing import Optional
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from rest_framework.authentication import BaseAuthentication

LOG = logging.getLogger(__name__)

APP_NAME = "osm-export-tool"


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


def find_legacy_user_by_osm_id(osm_id: int) -> Optional[User]:
    from social_django.models import UserSocialAuth
    try:
        social_auth = UserSocialAuth.objects.get(
            provider='openstreetmap-oauth2',
            uid=str(osm_id)
        )
        return social_auth.user
    except UserSocialAuth.DoesNotExist:
        return None


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


def api_login_required(view_func):
    """Like @login_required but returns 401 JSON instead of redirecting.
    Works with both AUTH_PROVIDER='hanko' and AUTH_PROVIDER='legacy'."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
            authenticated = is_hanko_authenticated(request)
        else:
            authenticated = request.user.is_authenticated
        if not authenticated:
            return JsonResponse({"error": "Not authenticated"}, status=401)
        return view_func(request, *args, **kwargs)
    return wrapper
