import json
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.admin.sites import site as admin_site
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import RequestFactory, TestCase, override_settings

from api.views import get_groups, get_user_permissions
from ui.hanko_helpers import is_hanko_admin
from ui.middleware import HankoUserMapMiddleware


class TestHankoUserMapMiddleware(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HankoUserMapMiddleware(
            get_response=lambda request: HttpResponse()
        )

    @patch("ui.middleware.get_mapped_django_user_by_hanko")
    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org,other@hotosm.org")
    def test_admin_email_sets_is_superuser_true(self, mock_get_user):
        mock_get_user.return_value = MagicMock()
        request = self.factory.get("/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.email = "admin@hotosm.org"
        self.middleware(request)
        self.assertTrue(request.user.is_superuser)

    @patch("ui.middleware.get_mapped_django_user_by_hanko")
    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_non_admin_email_sets_is_superuser_false(self, mock_get_user):
        mock_get_user.return_value = MagicMock()
        request = self.factory.get("/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.email = "regular@hotosm.org"
        self.middleware(request)
        self.assertFalse(request.user.is_superuser)

    @override_settings(AUTH_PROVIDER="hanko")
    def test_unauthenticated_does_not_set_request_user(self):
        request = self.factory.get("/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        self.middleware(request)
        self.assertFalse(hasattr(request, "user"))


class TestHankoAdminAccess(TestCase):
    """ADMIN_EMAILS has to grant access to Django's admin, not just permissions.

    The admin gates on is_staff; the navbar gates on auth.add_user, which
    is_superuser satisfies on its own. Granting only is_superuser therefore
    showed the Admin entry and then bounced the user
    /admin/ -> /admin/login/ -> /login/ -> /v3/ with nothing explaining why.
    """

    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = HankoUserMapMiddleware(
            get_response=lambda request: HttpResponse()
        )

    def run_middleware_for(self, user, email):
        request = self.factory.get("/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.email = email
        with patch("ui.middleware.get_mapped_django_user_by_hanko", return_value=user):
            self.middleware(request)
        return request

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_admin_email_can_actually_reach_the_django_admin(self):
        user = User.objects.create_user(username="listed", email="admin@hotosm.org")
        self.assertFalse(user.is_staff)

        request = self.run_middleware_for(user, "admin@hotosm.org")

        self.assertTrue(request.user.is_superuser)
        self.assertTrue(request.user.is_staff)
        admin_request = self.factory.get("/admin/")
        admin_request.user = request.user
        self.assertTrue(admin_site.has_permission(admin_request))

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_staff_in_the_database_keeps_admin_access(self):
        """Five production users have is_staff without being superusers. The
        list must add to that, never replace it."""
        user = User.objects.create_user(username="dbstaff", email="staff@hotosm.org")
        user.is_staff = True
        user.save()

        request = self.run_middleware_for(user, "staff@hotosm.org")

        self.assertFalse(request.user.is_superuser)
        self.assertTrue(request.user.is_staff)
        admin_request = self.factory.get("/admin/")
        admin_request.user = request.user
        self.assertTrue(admin_site.has_permission(admin_request))

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_regular_user_gets_neither(self):
        user = User.objects.create_user(username="regular", email="regular@hotosm.org")

        request = self.run_middleware_for(user, "regular@hotosm.org")

        self.assertFalse(request.user.is_superuser)
        self.assertFalse(request.user.is_staff)
        admin_request = self.factory.get("/admin/")
        admin_request.user = request.user
        self.assertFalse(admin_site.has_permission(admin_request))

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_admin_rights_are_not_persisted(self):
        """ADMIN_EMAILS grants per request; the database row stays untouched."""
        user = User.objects.create_user(username="ephemeral", email="admin@hotosm.org")

        self.run_middleware_for(user, "admin@hotosm.org")

        stored = User.objects.get(pk=user.pk)
        self.assertFalse(stored.is_superuser)
        self.assertFalse(stored.is_staff)


class TestGetUserPermissionsHanko(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # A real user: the non-superuser branch of the view queries Permission
        # against request.user, which a MagicMock cannot stand in for.
        self.user = User.objects.create_user(username="hankomapper")

    def _make_hanko_request(self, email, with_osm=False):
        request = self.factory.get("/api/user-permissions/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.email = email
        if with_osm:
            request.hotosm.osm = MagicMock()
            request.hotosm.osm.osm_username = "osmmapper"
        else:
            request.hotosm.osm = None
        # Simulate what the middlewares set: HankoAuthMiddleware exposes
        # request.hanko_user (what login_required checks), HankoUserMapMiddleware
        # maps it onto request.user.
        request.hanko_user = request.hotosm.user
        request.user = self.user
        request.user.is_superuser = is_hanko_admin(email)
        return request

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_unauthenticated_returns_401(self):
        request = self.factory.get("/api/user-permissions/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        request.hanko_user = None
        response = get_user_permissions(request)
        self.assertEqual(response.status_code, 401)

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_admin_is_superuser_true(self):
        request = self._make_hanko_request("admin@hotosm.org")
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertTrue(data["is_superuser"])

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_non_admin_is_superuser_false(self):
        request = self._make_hanko_request("regular@hotosm.org")
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertFalse(data["is_superuser"])

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_non_admin_permissions_empty(self):
        request = self._make_hanko_request("regular@hotosm.org")
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertEqual(data["permissions"], [])

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_username_from_email_when_no_osm(self):
        request = self._make_hanko_request("mapper@hotosm.org")
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertEqual(data["username"], "mapper")

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_username_from_osm_when_osm_present(self):
        request = self._make_hanko_request("mapper@hotosm.org", with_osm=True)
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertEqual(data["username"], "osmmapper")


class TestGetUserPermissionsLegacy(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="legacymapper")

    @override_settings(AUTH_PROVIDER="legacy")
    def test_unauthenticated_redirects_to_login(self):
        request = self.factory.get("/api/user-permissions/")
        request.user = MagicMock()
        request.user.is_authenticated = False
        response = get_user_permissions(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    @override_settings(AUTH_PROVIDER="legacy")
    def test_superuser_is_superuser_true(self):
        self.user.is_superuser = True
        self.user.save()
        request = self.factory.get("/api/user-permissions/")
        request.user = self.user
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertTrue(data["is_superuser"])

    @override_settings(AUTH_PROVIDER="legacy")
    def test_regular_user_is_superuser_false(self):
        request = self.factory.get("/api/user-permissions/")
        request.user = self.user
        response = get_user_permissions(request)
        data = json.loads(response.content)
        self.assertFalse(data["is_superuser"])


class TestGetGroups(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(AUTH_PROVIDER="hanko")
    def test_hanko_unauthenticated_returns_401(self):
        request = self.factory.get("/api/groups/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        request.hanko_user = None
        response = get_groups(request)
        self.assertEqual(response.status_code, 401)

    @override_settings(AUTH_PROVIDER="hanko")
    @patch("api.views.Group")
    def test_hanko_authenticated_returns_groups(self, mock_group):
        mock_group.objects.filter.return_value = []
        request = self.factory.get("/api/groups/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hanko_user = request.hotosm.user
        response = get_groups(request)
        data = json.loads(response.content)
        self.assertIn("groups", data)

    @override_settings(AUTH_PROVIDER="legacy")
    def test_legacy_unauthenticated_redirects_to_login(self):
        request = self.factory.get("/api/groups/")
        request.user = MagicMock()
        request.user.is_authenticated = False
        response = get_groups(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    @override_settings(AUTH_PROVIDER="legacy")
    @patch("api.views.Group")
    def test_legacy_authenticated_returns_groups(self, mock_group):
        mock_group.objects.filter.return_value = []
        request = self.factory.get("/api/groups/")
        request.user = MagicMock()
        request.user.is_authenticated = True
        response = get_groups(request)
        data = json.loads(response.content)
        self.assertIn("groups", data)


class TestLoginRequiredPerProvider(TestCase):
    """The decorator on api.views must honour the session under legacy.

    hotosm_auth_django's login_required only knows about request.hanko_user,
    which HankoAuthMiddleware sets and which does not exist under legacy — using
    it unconditionally locked every decorated view to 401 for logged-in users.
    """

    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(AUTH_PROVIDER="legacy")
    @patch("api.views.Group")
    def test_legacy_session_user_is_let_through(self, mock_group):
        mock_group.objects.filter.return_value = []
        request = self.factory.get("/api/groups/")
        request.user = MagicMock()
        request.user.is_authenticated = True
        # no request.hanko_user: the Hanko middleware is not installed here
        response = get_groups(request)
        self.assertEqual(response.status_code, 200)

    @override_settings(AUTH_PROVIDER="hanko")
    @patch("api.views.Group")
    def test_hanko_ignores_the_django_session(self, mock_group):
        """A Django session alone must not authenticate once Hanko is on."""
        mock_group.objects.filter.return_value = []
        request = self.factory.get("/api/groups/")
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.hanko_user = None
        response = get_groups(request)
        self.assertEqual(response.status_code, 401)


class TestRestFrameworkAuthenticators(TestCase):
    """Session auth is the only thing that authenticates the browser under
    legacy; it must stay in the DRF stack there and stay out under Hanko.

    Asserts against the provider the suite is actually running with, so run it
    both ways (AUTH_PROVIDER=legacy and AUTH_PROVIDER=hanko) to cover both.
    """

    def test_authenticators_match_the_configured_provider(self):
        classes = settings.REST_FRAMEWORK["DEFAULT_AUTHENTICATION_CLASSES"]
        session = "rest_framework.authentication.SessionAuthentication"
        hanko = "ui.hanko_helpers.HankoAuthentication"
        if settings.AUTH_PROVIDER == "hanko":
            self.assertIn(hanko, classes)
            self.assertNotIn(session, classes)
        else:
            self.assertIn(session, classes)
            self.assertNotIn(hanko, classes)
