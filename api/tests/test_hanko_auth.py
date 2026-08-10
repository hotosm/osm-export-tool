import json
from unittest.mock import MagicMock, patch

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


class TestGetUserPermissionsHanko(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

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
        # Simulate what HankoUserMapMiddleware sets on request.user
        request.user = MagicMock()
        request.user.is_superuser = is_hanko_admin(email)
        request.user.is_authenticated = True
        return request

    @override_settings(AUTH_PROVIDER="hanko", ADMIN_EMAILS="admin@hotosm.org")
    def test_unauthenticated_returns_401(self):
        request = self.factory.get("/api/user-permissions/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
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
    def test_unauthenticated_returns_401(self):
        request = self.factory.get("/api/user-permissions/")
        request.user = MagicMock()
        request.user.is_authenticated = False
        response = get_user_permissions(request)
        self.assertEqual(response.status_code, 401)

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
        response = get_groups(request)
        self.assertEqual(response.status_code, 401)

    @override_settings(AUTH_PROVIDER="hanko")
    @patch("api.views.Group")
    def test_hanko_authenticated_returns_groups(self, mock_group):
        mock_group.objects.filter.return_value = []
        request = self.factory.get("/api/groups/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        response = get_groups(request)
        data = json.loads(response.content)
        self.assertIn("groups", data)

    @override_settings(AUTH_PROVIDER="legacy")
    def test_legacy_unauthenticated_returns_401(self):
        request = self.factory.get("/api/groups/")
        request.user = MagicMock()
        request.user.is_authenticated = False
        response = get_groups(request)
        self.assertEqual(response.status_code, 401)

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
