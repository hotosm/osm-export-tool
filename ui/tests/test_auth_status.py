import json
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from ui.views import auth_status


class TestAuthStatusLegacy(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _make_request(self, authenticated=False):
        request = self.factory.get("/api/v1/auth/status/")
        request.hotosm = MagicMock()
        request.hotosm.user = None
        if authenticated:
            request.user = MagicMock()
            request.user.is_authenticated = True
        else:
            request.user = MagicMock()
            request.user.is_authenticated = False
        return request

    def test_unauthenticated_returns_legacy_provider(self):
        response = auth_status(self._make_request())
        data = json.loads(response.content)
        self.assertEqual(data["auth_provider"], "legacy")

    def test_unauthenticated_returns_false(self):
        response = auth_status(self._make_request())
        data = json.loads(response.content)
        self.assertFalse(data["authenticated"])

    def test_legacy_authenticated_user_returns_true(self):
        response = auth_status(self._make_request(authenticated=True))
        data = json.loads(response.content)
        self.assertTrue(data["authenticated"])

    def test_needs_onboarding_false_for_legacy(self):
        response = auth_status(self._make_request())
        data = json.loads(response.content)
        self.assertFalse(data["needs_onboarding"])


class TestAuthStatusHanko(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", email="test@example.com")

    def _make_hanko_request(self, osm_user_id=None):
        request = self.factory.get("/api/v1/auth/status/")
        request.user = MagicMock()
        request.user.is_authenticated = True
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.id = "hanko-uuid-abc"
        request.hotosm.user.email = "test@example.com"
        if osm_user_id is not None:
            request.hotosm.osm = MagicMock()
            request.hotosm.osm.osm_user_id = osm_user_id
        else:
            request.hotosm.osm = None
        return request

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_authenticated_returns_hanko_provider(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertEqual(data["auth_provider"], "hanko")

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_authenticated_returns_true(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertTrue(data["authenticated"])

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_no_osm_link_returns_osm_id_zero(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request(osm_user_id=None))
        data = json.loads(response.content)
        self.assertEqual(data["user"]["osm_id"], 0)

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_no_osm_link_is_real_osm_false(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request(osm_user_id=None))
        data = json.loads(response.content)
        self.assertFalse(data["user"]["is_real_osm"])

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_with_osm_link_returns_osm_id(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request(osm_user_id=12345))
        data = json.loads(response.content)
        self.assertEqual(data["user"]["osm_id"], 12345)

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_with_osm_link_is_real_osm_true(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request(osm_user_id=12345))
        data = json.loads(response.content)
        self.assertTrue(data["user"]["is_real_osm"])

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_authenticated_includes_hanko_user(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertIn("hanko_user", data)
        self.assertEqual(data["hanko_user"]["id"], "hanko-uuid-abc")

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_authenticated_includes_username(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertEqual(data["user"]["username"], "testuser")


class TestAuthStatusHankoOnboarding(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def _make_hanko_request(self):
        request = self.factory.get("/api/v1/auth/status/")
        request.user = MagicMock()
        request.hotosm = MagicMock()
        request.hotosm.user = MagicMock()
        request.hotosm.user.id = "hanko-uuid-new"
        request.hotosm.user.email = "new@example.com"
        return request

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_no_mapping_returns_hanko_provider(self, mock_mapped):
        mock_mapped.return_value = None
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertEqual(data["auth_provider"], "hanko")

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_no_mapping_authenticated_false(self, mock_mapped):
        mock_mapped.return_value = None
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertFalse(data["authenticated"])

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_no_mapping_needs_onboarding_true(self, mock_mapped):
        mock_mapped.return_value = None
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertTrue(data["needs_onboarding"])

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_no_mapping_includes_hanko_user(self, mock_mapped):
        mock_mapped.return_value = None
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertIn("hanko_user", data)
        self.assertEqual(data["hanko_user"]["id"], "hanko-uuid-new")

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_deleted_user_falls_to_onboarding(self, mock_mapped):
        mock_mapped.return_value = "99999"
        response = auth_status(self._make_hanko_request())
        data = json.loads(response.content)
        self.assertTrue(data["needs_onboarding"])
