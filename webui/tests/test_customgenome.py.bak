from django.test import TestCase, RequestFactory, Client
from django.core.management import call_command
import json

from . import base_fixtures as test_fixtures_set
from webui.models import CustomGenome

"""
Test custom genome models
"""

def setUpModule():
    for fixture in test_fixtures_set:
        full_fixture = 'webui/tests/test-data/' + fixture
        print "Loading fixture {}".format(full_fixture)
        call_command('loaddata', full_fixture, verbosity=1)
    

class CustomGenomeTest(TestCase):

    def setUp(self):
#         for fixture in self.test_fixtures:
#             full_fixture = 'webui/tests/test-data/' + fixture
#             print "Loading fixture {}".format(full_fixture)
#             call_command('loaddata', full_fixture, verbosity=1)

        self.factory = RequestFactory()

    def testProperties(self):

        cg = CustomGenome.objects.get(pk=1)
        
        self.assertEquals(cg.is_system_owned, False, "Custom Genome is not system owner")

        self.assertEqual(cg.isvalid, True, 'Custom Genome is valid')

        self.assertEqual(cg.is_owner(3), True, "User 3 owner the custom genome")

        self.assertEqual(cg.contigs, 1, 'Test Custom Genomes only has 1 contig')
