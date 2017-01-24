import requests, sys
from requests_toolbelt.multipart.encoder import MultipartEncoder

 
server = "http://localhost:8000"
ext = "/islandviewer/rest/job/submit/"

genome_file="mygenome.gbk"

multipart_data = MultipartEncoder(
    fields={ "format_type": "GENBANK",
             'email_addr': 'my@email.address.com',
#  For incomplete genomes include a reference accession
#             'ref_accnum': 'NC_022792.1',
             'genome_file': ('filename', open(mygenome, 'rb'), 'text/plain')}
)
headers={'Content-Type': multipart_data.content_type,
         'x-authtoken': 'e75bea25-313f-05f2-2887-259746586857'}

r = requests.post(server+ext, headers=headers, data=multipart_data)
 
if not r.ok:
  r.raise_for_status()
  sys.exit()
 
decoded = r.json()
print repr(decoded)
 
