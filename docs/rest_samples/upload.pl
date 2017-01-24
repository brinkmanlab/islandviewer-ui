#!/usr/bin/perl
print "Content-type: text/html\n\n";
 
use HTTP::Request::Common;
use LWP::UserAgent;
use CGI qw(:standard);
use strict;
use warnings;
 
my ($file, $result, $message);
 
$file = "tiny.gbk";
 
my $ua = LWP::UserAgent->new;
my $req = $ua->request(POST 'http://localhost:8000/islandviewer/rest/job/submit/',
          (Content_Type => 'form-data',
	   'x-authtoken' => 'e75bea25-313f-05f2-2887-259746586857' ),
          Content => [
        email_addr => 'my@email.address.com',
        format_type => "GENBANK",
        genome_name => "my sample genome",
        genome_file => ["$file"],
#  For incomplete genomes include a reference accession
#        ref_accnum => "NC_022792.1"
          ]
);
 
print "\nRESPONSE -- \n" . $req->as_string;
 
# Check the outcome of the response
if ($req->is_success) {
    print $req->content;
}
else {
  print "\n in else not success\n";
}
