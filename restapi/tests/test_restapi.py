from django.test import TestCase, RequestFactory, Client
from django.core.management import call_command
from django.core.urlresolvers import reverse
import os, json, pprint

from webui.tests import analysis_fixtures, microbedb_fixtures
from webui.models import UserToken

"""
Test rest api calls
"""

REF_FILE_PATH = os.path.join(os.path.dirname(__file__), 'references')
WRITE_REFS = False

def setUpModule():
    for fixture in analysis_fixtures + microbedb_fixtures:
        full_fixture = 'webui/tests/test-data/' + fixture
        print "Loading fixture {}".format(full_fixture)
        call_command('loaddata', full_fixture, verbosity=1)

class RestAPITest(TestCase):
    def fetch_usertoken(self, uid):
        usertoken = UserToken.objects.get(pk=uid)
        return usertoken.token

    def testREST(self):
        print "Testing REST endpoints"
        token = self.fetch_usertoken(1)

        url = reverse('restapi:user_jobs')
        self.jsonFetch(url, "all_jobs", token, WRITE_REFS)

        url = reverse('restapi:user_job', kwargs={'aid': 12})
        self.jsonFetch(url, "job_12", token, WRITE_REFS)

        url = reverse('restapi:user_job_islandpick', kwargs={'aid': 14})
        self.jsonFetch(url, "islandpick_14", token, WRITE_REFS)

        url = reverse('restapi:user_job_download', kwargs={'aid': 14, 'format': 'genbank'})
        self.textFetch(url, "download_gbk_14", token, WRITE_REFS)

        url = reverse('restapi:user_job_download', kwargs={'aid': 14, 'format': 'fasta'})
        self.textFetch(url, "download_fasta_14", token, WRITE_REFS)

        url = reverse('restapi:ref_genomes')
        self.jsonFetch(url, "ref_genomes", token, WRITE_REFS)

    def testToken(self):
        print "Testing REST authentication"
        c = Client()

        url = reverse('restapi:user_jobs')
        
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN='abcde')
        self.assertEqual(response.status_code, 401, "Bad REST token")

        token = self.fetch_usertoken(2)
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        self.assertEqual(response.status_code, 401, "Expired REST token")

        token = self.fetch_usertoken(3)
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        self.assertEqual(response.status_code, 401, "Inactive user")

        token = self.fetch_usertoken(1)
        url = reverse('restapi:user_job', kwargs={'aid': 15})
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        self.assertEqual(response.status_code, 401, "User doesn't own job")

        url = reverse('restapi:user_job_download', kwargs={'aid': 13, 'format': 'genbank'})
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        self.assertEqual(response.status_code, 204, "Job not finished running")

        url = reverse('restapi:user_job_download', kwargs={'aid': 15, 'format': 'genbank'})
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        self.assertEqual(response.status_code, 401, "User doesn't own job (download)")

        url = reverse('restapi:user_job_download', kwargs={'aid': 14, 'format': 'zoom'})
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        self.assertEqual(response.status_code, 400, "Download format doesn't exist")

    def jsonFetch(self, url, slug, token, write_ref=False):
        print "\tREST API: {}".format(url)
        
        c = Client()
        json_filename = os.path.join( REF_FILE_PATH, "rest_{}.json".format(slug))
        
        if not write_ref:
            json_file = open( json_filename)
            refs = json.load(json_file)
            
        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        response_json = response.json()

        if write_ref:
            self.writeRef(json_filename, response_json)
        else:
            self.assertEqual(refs, response_json, "URL: {}, test: {}".format(url, slug))

    def textFetch(self, url, slug, token, write_ref=False):
        print "\tREST API: {}".format(url)
        c = Client()
        text_filename = os.path.join( REF_FILE_PATH, "rest_{}.txt".format(slug))

        if not write_ref:
            with open(text_filename, "r") as txtfile:
                refs = ''.join(line for line in txtfile)

        response = c.get(url,
                         None,
                         HTTP_X_AUTHTOKEN=token)
        response_content = response.content

        if write_ref:
            self.writeText(text_filename, response_content)
        else:
            self.assertEqual(refs, response_content, "URL: {}, test: {}".format(url, slug))        
        
    def writeRef(self, filename, ref):
        print "\tWriting reference file {}".format(filename)
        with open(filename, 'w') as outfile:
            json.dump(ref, outfile, sort_keys=True, indent=4)

    def writeText(self, filename, ref):
        print "\tWriting reference file {}".format(filename)
        with open(filename, 'w') as outfile:
            outfile.write(ref)
