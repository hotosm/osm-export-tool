# -*- coding: utf-8 -*-
"""Hanko authentication helper utilities for osm-export-tool."""

import logging
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication

LOG = logging.getLogger(__name__)


class HankoAuthentication(BaseAuthentication):
    """
    DRF authentication class that bridges Hanko middleware to DRF.

    The HankoAuthMiddleware sets request.hotosm.user for every request.
    This class makes DRF aware of that authentication so that
    DRF's IsAuthenticated permission and request.user work correctly.
    """

    def authenticate(self, request):
        if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
            return None

        if not hasattr(request, 'hotosm') or not request._request.hotosm.user:
            return None

        # Map the Hanko user to a Django User
        hanko_user = request._request.hotosm.user
        osm_connection = getattr(request._request.hotosm, 'osm', None)
        django_user = get_or_create_mapped_user(hanko_user, osm_connection)

        return (django_user, None)


def get_or_create_mapped_user(hanko_user, osm_connection=None):
    """
    Get or create a Django User mapped to a Hanko user.

    Uses the hanko_user_mappings table (via hotosm_auth_django) to persist
    the relationship between Hanko user IDs and Django user IDs.

    Flow:
    1. Check hanko_user_mappings table for existing mapping
    2. If mapped, load the Django User by ID
    3. If not mapped, find existing Django user by email or OSM username
    4. If found, create a mapping in hanko_user_mappings
    5. If not found, create a new Django user and then create a mapping

    Args:
        hanko_user: The Hanko user object (with .id and .email)
        osm_connection: Optional OSM connection (with .osm_username)

    Returns:
        User: The Django User object
    """
    from hotosm_auth_django.middleware import get_mapped_user_id, create_user_mapping

    APP_NAME = "osm-export-tool"

    # 1. Check hanko_user_mappings for existing mapping
    mapped_user_id = get_mapped_user_id(hanko_user, app_name=APP_NAME)
    if mapped_user_id:
        try:
            user = User.objects.get(pk=int(mapped_user_id))
            LOG.debug(f"Found mapped user: hanko={hanko_user.id} -> django={user.pk}")
            return user
        except (User.DoesNotExist, ValueError):
            LOG.warning(f"Mapping exists but user not found: {mapped_user_id}")

    # 2. No mapping yet — try to find existing Django user by email
    user = None
    email = hanko_user.email if hanko_user else None

    if email:
        try:
            user = User.objects.get(email__iexact=email)
            LOG.debug(f"Found user by email: {email}")
        except User.DoesNotExist:
            pass
        except User.MultipleObjectsReturned:
            user = User.objects.filter(email__iexact=email).first()
            LOG.warning(f"Multiple users found with email: {email}")

    # 3. Try to find by OSM username
    if not user and osm_connection:
        osm_username = getattr(osm_connection, 'osm_username', None)
        if osm_username:
            try:
                user = User.objects.get(username__iexact=osm_username)
                LOG.debug(f"Found user by OSM username: {osm_username}")
            except User.DoesNotExist:
                pass

    # 4. Create new Django user if not found
    if not user:
        username = email.split('@')[0] if email else f"hanko_{hanko_user.id[:8]}"
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email or "",
        )
        LOG.info(f"Created new Django user for Hanko user: {username}")

    # 5. Create mapping in hanko_user_mappings table
    try:
        create_user_mapping(
            hanko_user_id=hanko_user.id,
            app_user_id=str(user.pk),
            app_name=APP_NAME,
        )
        LOG.info(f"Created user mapping: hanko={hanko_user.id} -> django={user.pk}")
    except Exception as e:
        # Mapping may already exist (race condition) — that's fine
        LOG.debug(f"Could not create mapping (may already exist): {e}")

    return user


def get_mapped_django_user(request):
    """
    Get the Django User mapped to the current Hanko user.

    Args:
        request: Django request object with hotosm attribute

    Returns:
        User or None: The mapped Django User or None
    """
    if not is_hanko_authenticated(request):
        return None

    hanko_user = request.hotosm.user
    osm_connection = getattr(request.hotosm, 'osm', None)

    return get_or_create_mapped_user(hanko_user, osm_connection)


class HankoUserFilterMixin:
    """
    Mixin that filters querysets by the mapped Hanko user.

    Use this mixin in ViewSets that need to filter data by the current
    authenticated user when using Hanko SSO.

    Example:
        class JobViewSet(HankoUserFilterMixin, viewsets.ModelViewSet):
            queryset = Job.objects.all()
            serializer_class = JobSerializer
    """

    def get_queryset(self):
        qs = super().get_queryset()

        # Only filter if using Hanko authentication
        if getattr(settings, 'AUTH_PROVIDER', 'legacy') != 'hanko':
            return qs

        if hasattr(self.request, 'hotosm') and self.request.hotosm.user:
            from hotosm_auth_django import get_mapped_user_id
            app_user_id = get_mapped_user_id(
                self.request.hotosm.user,
                app_name="osm-export-tool"
            )
            if app_user_id:
                # Filter by user_id field (used in Job and SavedFeatureSelection models)
                return qs.filter(user_id=app_user_id)

        return qs


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


def get_hanko_user(request):
    """
    Get the Hanko user from the request.

    Args:
        request: Django request object

    Returns:
        HankoUser or None: The authenticated Hanko user or None
    """
    if is_hanko_authenticated(request):
        return request.hotosm.user
    return None


def get_osm_connection(request):
    """
    Get the OSM connection from the request (if available).

    Args:
        request: Django request object

    Returns:
        OSMConnection or None: The OSM connection or None
    """
    if is_hanko_authenticated(request) and hasattr(request.hotosm, 'osm'):
        return request.hotosm.osm
    return None


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


def require_osm_connection(view_func):
    """
    Decorator that requires both Hanko authentication and OSM connection.

    Use this decorator on function-based views that require OSM connection
    (e.g., for creating exports that need OSM credentials).

    Example:
        @require_osm_connection
        def my_osm_view(request):
            osm = request.hotosm.osm
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
            if not get_osm_connection(request):
                return JsonResponse(
                    {"error": "OSM connection required"},
                    status=403
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
