from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase

from ui.hanko_helpers import (
    HankoAuthentication,
    create_export_tool_user,
    find_legacy_user_by_email,
    find_legacy_user_by_osm_id,
    get_mapped_django_user_by_hanko,
    is_hanko_authenticated,
)


class TestIsHankoAuthenticated(TestCase):
    def test_returns_true_when_hotosm_user_present(self):
        request = MagicMock()
        request.hotosm.user = MagicMock()
        self.assertTrue(is_hanko_authenticated(request))

    def test_returns_false_when_hotosm_missing(self):
        request = object()
        self.assertFalse(is_hanko_authenticated(request))

    def test_returns_false_when_hotosm_user_is_none(self):
        request = MagicMock()
        request.hotosm.user = None
        self.assertFalse(is_hanko_authenticated(request))


class TestGetMappedDjangoUserByHanko(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="mapper", email="mapper@example.com")
        self.hanko_user = MagicMock()
        self.hanko_user.id = "hanko-abc-123"

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_returns_user_when_mapping_exists(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        result = get_mapped_django_user_by_hanko(self.hanko_user)
        self.assertEqual(result, self.user)

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_returns_none_when_no_mapping(self, mock_mapped):
        mock_mapped.return_value = None
        result = get_mapped_django_user_by_hanko(self.hanko_user)
        self.assertIsNone(result)

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_returns_none_when_mapped_user_deleted(self, mock_mapped):
        mock_mapped.return_value = "99999"
        result = get_mapped_django_user_by_hanko(self.hanko_user)
        self.assertIsNone(result)


class TestFindLegacyUserByOsmId(TestCase):
    """Uses real UserSocialAuth rows: the provider names and the ordering are
    the whole point here, and a mocked manager would assert nothing about them.
    """

    def setUp(self):
        from social_django.models import UserSocialAuth

        self.UserSocialAuth = UserSocialAuth
        self.user = User.objects.create_user(username="osmuser")

    def connect(self, user, osm_id, provider="openstreetmap-oauth2"):
        return self.UserSocialAuth.objects.create(
            user=user, provider=provider, uid=str(osm_id)
        )

    def test_finds_user_connected_with_the_current_provider(self):
        self.connect(self.user, 12345)
        self.assertEqual(find_legacy_user_by_osm_id(12345), self.user)

    def test_finds_user_connected_with_the_oauth1_provider(self):
        """55k production accounts predate openstreetmap-oauth2 and are still
        stored under `openstreetmap`. Missing them sent 55% of users to the
        email fallback, which only works if their Hanko email happens to match.
        """
        self.connect(self.user, 12345, provider="openstreetmap")
        self.assertEqual(find_legacy_user_by_osm_id(12345), self.user)

    def test_prefers_the_current_provider_when_an_account_has_both(self):
        old_account = User.objects.create_user(username="old")
        self.connect(old_account, 12345, provider="openstreetmap")
        self.connect(self.user, 12345)
        self.assertEqual(find_legacy_user_by_osm_id(12345), self.user)

    def test_duplicate_accounts_resolve_deterministically(self):
        """630 uids in production point at two different users — one account per
        provider, since (provider, uid) is unique. Whatever we return, it has to
        be the same user every time and never an exception.
        """
        other = User.objects.create_user(username="duplicate")
        self.connect(other, 12345, provider="openstreetmap")
        self.connect(self.user, 12345)
        self.assertEqual(find_legacy_user_by_osm_id(12345), self.user)
        self.assertEqual(find_legacy_user_by_osm_id(12345), self.user)

    def test_ignores_other_providers(self):
        self.connect(self.user, 12345, provider="google-oauth2")
        self.assertIsNone(find_legacy_user_by_osm_id(12345))

    def test_returns_none_when_no_osm_connection(self):
        self.assertIsNone(find_legacy_user_by_osm_id(99999))


class TestFindLegacyUserByEmail(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="emailuser", email="legacy@example.com")

    def test_returns_user_when_email_matches(self):
        result = find_legacy_user_by_email("legacy@example.com")
        self.assertEqual(result, self.user)

    def test_returns_none_when_email_not_found(self):
        result = find_legacy_user_by_email("unknown@example.com")
        self.assertIsNone(result)

    def test_returns_none_for_empty_email(self):
        result = find_legacy_user_by_email("")
        self.assertIsNone(result)

    def test_returns_none_for_none_email(self):
        result = find_legacy_user_by_email(None)
        self.assertIsNone(result)


class TestCreateExportToolUser(TestCase):
    def test_creates_user_with_given_username(self):
        user = create_export_tool_user(username="newmapper", email="new@example.com")
        self.assertEqual(user.username, "newmapper")
        self.assertEqual(user.email, "new@example.com")

    def test_resolves_username_conflict_with_suffix(self):
        User.objects.create_user(username="mapper")
        user = create_export_tool_user(username="mapper")
        self.assertEqual(user.username, "mapper_1")

    def test_resolves_multiple_conflicts_incrementally(self):
        User.objects.create_user(username="mapper")
        User.objects.create_user(username="mapper_1")
        user = create_export_tool_user(username="mapper")
        self.assertEqual(user.username, "mapper_2")

    def test_creates_user_without_email(self):
        user = create_export_tool_user(username="noemail")
        self.assertEqual(user.email, "")


class TestHankoAuthentication(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="hankouser", email="hanko@example.com")
        self.auth = HankoAuthentication()

    def _make_request(self, hanko_user=None):
        request = MagicMock()
        inner = MagicMock()
        if hanko_user is not None:
            inner.hotosm.user = hanko_user
        else:
            inner.hotosm.user = None
        request._request = inner
        return request

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_returns_user_when_mapped(self, mock_mapped):
        mock_mapped.return_value = str(self.user.id)
        hanko_user = MagicMock()
        hanko_user.id = "hanko-uuid"
        result = self.auth.authenticate(self._make_request(hanko_user=hanko_user))
        self.assertEqual(result, (self.user, None))

    @patch("hotosm_auth_django.get_mapped_user_id")
    def test_returns_none_when_no_mapping(self, mock_mapped):
        mock_mapped.return_value = None
        hanko_user = MagicMock()
        result = self.auth.authenticate(self._make_request(hanko_user=hanko_user))
        self.assertIsNone(result)

    def test_returns_none_when_no_hotosm_user(self):
        result = self.auth.authenticate(self._make_request(hanko_user=None))
        self.assertIsNone(result)
