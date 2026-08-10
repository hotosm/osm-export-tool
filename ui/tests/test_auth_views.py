import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings

from ui.views import auth_me, onboarding_callback


class TestAuthMe(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="exporter", email="exporter@example.com")

    def _make_hanko_request(self, with_osm=False):
        request = self.factory.get("/api/auth/me/")
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.id = "hanko-uuid-xyz"
        if with_osm:
            request.hotosm.osm = MagicMock()
            request.hotosm.osm.osm_username = "osmexporter"
            request.hotosm.osm.osm_user_id = 54321
        else:
            request.hotosm.osm = None
        return request

    @patch("ui.views.get_mapped_django_user")
    def test_hanko_authenticated_returns_user_data(self, mock_mapped):
        mock_mapped.return_value = self.user
        response = auth_me(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertEqual(data["user_id"], self.user.id)
        self.assertEqual(data["username"], "exporter")

    @patch("ui.views.get_mapped_django_user")
    def test_hanko_with_osm_includes_osm_fields(self, mock_mapped):
        mock_mapped.return_value = self.user
        response = auth_me(self._make_hanko_request(with_osm=True))
        data = json.loads(response.content)
        self.assertEqual(data["osm_username"], "osmexporter")
        self.assertEqual(data["osm_user_id"], 54321)

    @patch("ui.views.get_mapped_django_user")
    def test_hanko_not_mapped_returns_401(self, mock_mapped):
        mock_mapped.return_value = None
        response = auth_me(self._make_hanko_request())
        self.assertEqual(response.status_code, 401)

    def test_legacy_authenticated_returns_user_data(self):
        request = self.factory.get("/api/auth/me/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        request.user = self.user
        response = auth_me(request)
        data = json.loads(response.content)
        self.assertEqual(data["username"], "exporter")

    def test_unauthenticated_returns_401(self):
        request = self.factory.get("/api/auth/me/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        request.user = MagicMock()
        request.user.is_authenticated = False
        response = auth_me(request)
        self.assertEqual(response.status_code, 401)


@override_settings(AUTH_PROVIDER="hanko", HANKO_PUBLIC_URL="https://dev.login.hotosm.org")
class TestOnboardingCallbackNewUser(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, new_user="true", osm_connection=None):
        request = self.factory.get("/api/v1/auth/onboarding/", {"new_user": new_user})
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.id = "hanko-new-abc"
        request.hotosm.user.email = "newuser@example.com"
        request.hotosm.osm = osm_connection
        return request

    @patch("hotosm_auth_django.get_mapped_user_id", return_value=None)
    @patch("hotosm_auth_django.create_user_mapping")
    def test_new_user_creates_django_user(self, mock_create_mapping, mock_mapped):
        request = self._make_request()
        onboarding_callback(request)
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    @patch("hotosm_auth_django.get_mapped_user_id", return_value=None)
    @patch("hotosm_auth_django.create_user_mapping")
    def test_new_user_redirects_to_v3(self, mock_create_mapping, mock_mapped):
        request = self._make_request()
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/v3/")

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_existing_mapping_skips_creation_and_redirects(self, mock_mapped):
        user = User.objects.create_user(username="existing")
        mock_mapped.return_value = str(user.id)
        request = self._make_request()
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/v3/")

    @patch("hotosm_auth_django.get_mapped_user_id", return_value=None)
    @patch("hotosm_auth_django.create_user_mapping")
    @patch("ui.views.find_legacy_user_by_osm_id")
    def test_new_user_with_osm_links_existing_account(self, mock_find_osm, mock_create_mapping, mock_mapped):
        existing = User.objects.create_user(username="legacymapper")
        mock_find_osm.return_value = existing
        osm_connection = MagicMock()
        osm_connection.osm_user_id = 99
        request = self._make_request(osm_connection=osm_connection)
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        mock_create_mapping.assert_called_once()


@override_settings(AUTH_PROVIDER="hanko", HANKO_PUBLIC_URL="https://dev.login.hotosm.org")
class TestOnboardingCallbackLegacyUser(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="legacymapper", email="legacy@example.com")

    def _make_request(self, osm_connection=None):
        request = self.factory.get("/api/v1/auth/onboarding/", {"new_user": "false"})
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.id = "hanko-legacy-xyz"
        request.hotosm.user.email = "legacy@example.com"
        request.hotosm.osm = osm_connection
        return request

    @patch("hotosm_auth_django.get_auth_config")
    def test_no_osm_connection_redirects_to_login_service(self, mock_config):
        mock_config.return_value.osm_enabled = False
        request = self._make_request(osm_connection=None)
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("dev.login.hotosm.org", response.url)

    @patch("hotosm_auth_django.create_user_mapping")
    @patch("ui.views.find_legacy_user_by_osm_id")
    def test_found_by_osm_id_creates_mapping_and_redirects(self, mock_find, mock_create_mapping):
        mock_find.return_value = self.user
        osm_connection = MagicMock()
        osm_connection.osm_user_id = 777
        request = self._make_request(osm_connection=osm_connection)
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/v3/")

    @patch("hotosm_auth_django.create_user_mapping")
    @patch("ui.views.find_legacy_user_by_osm_id", return_value=None)
    @patch("ui.views.find_legacy_user_by_email")
    def test_not_found_by_osm_falls_back_to_email(self, mock_email, mock_osm, mock_create):
        mock_email.return_value = self.user
        osm_connection = MagicMock()
        osm_connection.osm_user_id = 888
        request = self._make_request(osm_connection=osm_connection)
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/v3/")

    @patch("ui.views.find_legacy_user_by_osm_id", return_value=None)
    @patch("ui.views.find_legacy_user_by_email", return_value=None)
    def test_no_existing_account_redirects_with_error(self, mock_email, mock_osm):
        osm_connection = MagicMock()
        osm_connection.osm_user_id = 999
        request = self._make_request(osm_connection=osm_connection)
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 302)
        self.assertIn("no_existing_osm_account", response.url)


class TestOnboardingCallbackGuards(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(AUTH_PROVIDER="legacy")
    def test_rejects_when_not_hanko_provider(self):
        request = self.factory.get("/api/v1/auth/onboarding/")
        request.hotosm = MagicMock()
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 400)

    @override_settings(AUTH_PROVIDER="hanko")
    def test_rejects_unauthenticated_hanko_request(self):
        request = self.factory.get("/api/v1/auth/onboarding/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        response = onboarding_callback(request)
        self.assertEqual(response.status_code, 401)
