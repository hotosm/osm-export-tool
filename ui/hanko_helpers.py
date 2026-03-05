# -*- coding: utf-8 -*-
"""Hanko authentication helper utilities for osm-export-tool.

These helpers implement the user mapping flow for osm-export-tool:
1. Check if mapping exists (hanko_id → user_id)
2. If not, redirect to onboarding
3. Legacy user → Connect OSM to recover account (lookup by OSM ID)
4. New user → Create new Django user
"""

import logging
from typing import Optional
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication

LOG = logging.getLogger(__name__)

APP_NAME = "osm-export-tool"


class HankoAuthentication(BaseAuthentication):
    """
    DRF authentication class that bridges Hanko middleware to DRF.

    The HankoAuthMiddleware sets request.hotosm.user for every request.
    This class makes DRF aware of that authentication so that
    DRF's IsAuthenticated permission and request.user work correctly.

    IMPORTANT: This does NOT auto-create users or mappings. If no mapping
    exists, the user needs to complete onboarding first.
    """

    def authenticate(self, request):
        if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
            return None

        if not hasattr(request, 'hotosm') or not request._request.hotosm.user:
            return None

        # Only return user if mapping exists - no auto-creation
        hanko_user = request._request.hotosm.user
        django_user = get_mapped_django_user_by_hanko(hanko_user)

        if django_user:
            return (django_user, None)

        # No mapping - user needs onboarding
        # Return None so DRF treats as unauthenticated
        return None


def get_mapped_django_user_by_hanko(hanko_user) -> Optional[User]:
    """
    Get the Django User mapped to a Hanko user.

    Only returns a user if a mapping already exists. Does NOT auto-create
    mappings or users. The onboarding flow handles user/mapping creation.

    Args:
        hanko_user: The Hanko user object (with .id and .email)

    Returns:
        User or None: The mapped Django User or None if no mapping exists
    """
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
    """Find existing user by OSM ID via social_auth.

    Used after OSM connect to check if this OSM ID already exists
    in the database (legacy user). This is more reliable than username
    because OSM allows username changes.

    Args:
        osm_id: OSM user ID from OAuth

    Returns:
        User if found, None otherwise
    """
    try:
        from social_django.models import UserSocialAuth
        social_auth = UserSocialAuth.objects.get(
            provider='openstreetmap-oauth2',
            uid=str(osm_id)
        )
        return social_auth.user
    except Exception:
        return None


def find_legacy_user_by_email(email: str) -> Optional[User]:
    """Find existing user by email.

    Used as fallback when OSM ID lookup fails. More reliable than username
    because email is unique and doesn't change as often.

    Note: Legacy users from OSM OAuth typically don't have email set
    (OSM OAuth returns email=""). This only works if user manually
    configured their email in export tool.

    Args:
        email: Email address to search for

    Returns:
        User if found, None otherwise
    """
    if not email:
        return None
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


def create_export_tool_user(
    username: str,
    email: Optional[str] = None,
) -> User:
    """Create a new Django User for export tool.

    Args:
        username: Display username
        email: Email address (optional)

    Returns:
        User: Created user instance
    """
    # Handle username conflicts by appending suffix
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
    """
    Get the Django User mapped to the current Hanko user.

    Only returns a user if a mapping already exists. Does NOT auto-create.

    Args:
        request: Django request object with hotosm attribute

    Returns:
        User or None: The mapped Django User or None
    """
    if not is_hanko_authenticated(request):
        return None

    hanko_user = request.hotosm.user
    return get_mapped_django_user_by_hanko(hanko_user)


def is_hanko_authenticated(request):
    """
    Check if the request is authenticated via Hanko SSO.

    Args:
        request: Django request object

    Returns:
        bool: True if authenticated via Hanko, False otherwise
    """
    if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
        return False
    return hasattr(request, 'hotosm') and request.hotosm.user is not None


def require_hanko_auth(view_func):
    """
    Decorator that requires Hanko authentication.

    Use this decorator on function-based views that require authentication
    when using Hanko SSO.

    Example:
        @require_hanko_auth
        def my_protected_view(request):
            ...
    """
    from functools import wraps
    from django.http import JsonResponse

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if getattr(settings, 'AUTH_PROVIDER', 'legacy') == 'hanko':
            if not is_hanko_authenticated(request):
                return JsonResponse(
                    {"error": "Not authenticated"},
                    status=401
                )
        else:
            # Fall back to Django's built-in authentication
            if not request.user.is_authenticated:
                return JsonResponse(
                    {"error": "Not authenticated"},
                    status=401
                )
        return view_func(request, *args, **kwargs)
    return wrapper
