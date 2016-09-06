# -*- coding: utf-8 -*-
import logging

from mock import patch

from django.contrib.auth.models import Group, User
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.test import TestCase

from rest_framework.authtoken.models import Token
from rest_framework.reverse import reverse

from oet2.api.validators import get_geodesic_area, validate_bbox
from oet2.jobs.models import ExportProfile

logger = logging.getLogger(__name__)


class TestValidators(TestCase):

    def setUp(self,):
        self.user = User.objects.create_user(
            username='demo1', email='demo@demo.com', password='demo'
        )
        self.extents = (13.473475, 7.441068, 24.002661, 23.450369)

    def test_validate_bbox(self,):
        validate_bbox(self.extents, user=self.user)

    def test_get_geodesic_area(self,):
        bbox = GEOSGeometry(Polygon.from_bbox(self.extents), srid=4326)
        area = get_geodesic_area(bbox)
        self.assertEquals(2006874.9259034647, area / 1000000)
