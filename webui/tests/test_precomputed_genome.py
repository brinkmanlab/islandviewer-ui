from django.test import TestCase, RequestFactory, Client
from django.core.management import call_command
import json

from . import base_fixtures, namecache_fixtures, microbedb_fixtures
from webui.models import NameCache, Analysis

"""
Test custom genome models
"""

def setUpModule():
    for fixture in base_fixtures + namecache_fixtures + microbedb_fixtures:
        full_fixture = 'webui/tests/test-data/' + fixture
        print "Loading fixture {}".format(full_fixture)
        call_command('loaddata', full_fixture, verbosity=1)
    

class NameCacheTest(TestCase):

    def testNameCache(self):

        genome = NameCache.objects.get(pk=1978)

        self.assertEqual(genome.owner_id, 0, 'Test owner is 0')
        self.assertEqual(genome.is_owner(3), False, "Assert MicrobeDB genomes have no owner")
        self.assertEqual(genome.is_system_owned, True, "Assert MicrobeDB are system owned")
        self.assertEqual(genome.contigs, 1, "MicrobeDB genomes only have 1 contig")
        self.assertEqual(genome.genome_status, 6, "MicrobeDB genomes are READY (6)")
        
    def testLookup(self):

        genome = Analysis.lookup_genome('NC_002516.2')

        self.assertEqual(genome.name, "Pseudomonas aeruginosa PAO1 chromosome, complete genome.", "Lookup should have returned PAO1")
        
    def testMicrobeDBLinkage(self):

        genome = NameCache.objects.get(pk=1978)

        self.assertEqual(genome.filename, "/data/NCBI_genomes/MicrobeDBv2/Bacteria_2016-12-15/Pseudomonas_aeruginosa/GCF_000006765.1_ASM676v1/NC_002516", "Check filename received from MicrobeDB")
        self.assertEqual(genome.formats, ".faa .ffn .fna .gbk .ptt", "Ensure MicrobeDB returns formats correctly")
