from django.test import TestCase, RequestFactory
from django.contrib.auth.models import AnonymousUser, User
from django.core.management import call_command
import json

from . import base_fixtures
from webui.views import results, runstatus

"""
Test custom genome models
"""

def setUpModule():
    for fixture in base_fixtures:
        full_fixture = 'webui/tests/test-data/' + fixture
        print "Loading fixture {}".format(full_fixture)
        call_command('loaddata', full_fixture, verbosity=1)
    

class AuthTest(TestCase):
    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
#        self.user = User.objects.create_user(
#            username='zerocool', email='mewiththebest@dieliketherest.com', password='top_secret')

    def testStatusAuthentication(self):
        print "Test status authentication on views"

        request = self.factory.get('/tark/status/')

        request.user = self.fetch_user(2)
        response = runstatus(request)
        self.assertEqual(response.status_code, 200, "Staff has access to status")

        request.user = self.fetch_user(3)
        response = runstatus(request)
        self.assertEqual(response.status_code, 401, "Non-staff can't access status")

        request.user = AnonymousUser()
        response = runstatus(request)
        self.assertEqual(response.status_code, 401, "Anonymous users can't access status")

    def fetch_user(self, uid):
        user = User.objects.get(pk=uid)

        return user
