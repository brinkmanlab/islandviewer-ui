import os.path
import subprocess
import base64
import pprint
from webui.models import UploadGenome
from django.conf import settings
from Bio import SeqIO
from uploadparser import submitter

class GenomeParser():
        
    def submitUpload(self, file, format_type, name, email_addr, uploader_ip, user_id = None, **kwargs):
        '''
        We're going to accept an uploaded file and
        put it in the uploads directory with an
        autoinc filename then send this to the
        backend for processing
        '''
        
        # Make the filename with the correct format
        genome_format = ''
        if format_type == 'GENBANK':
            genome_format += 'gbk'
        else:
            genome_format += 'embl'

        # Create the output file and write out the upload
        # No, we're going to do the tests in the backend now
        g_name = "Custom Genome"
        if name:
            g_name = name

        try:
            genome_data = file.read()
            ret = submitter.send_job(genome_data, genome_format, g_name, email_addr, uploader_ip, user_id, **kwargs)
        except Exception as e:
            if settings.DEBUG:
                debug_error = ''
                for arg in e.args:
                    print "{0}\n".format(arg)
                    debug_error += arg
                raise Exception("Unknown error: " + debug_error)

            raise Exception("Unknown error")

        if settings.DEBUG:
            pprint.pprint(ret)
                
        
        return ret;
    
    def submitCustom(self, form_data, uploader_ip, user_id = None):
        '''
        We're going to take the form data and determine what we need to send based
        on the fields we've received, is this an initial upload or a continuation
        of a previous one because pieces were missing
        '''
           
        if 'cid' in form_data and form_data['cid'] > 0:
            '''
            We're a returning upload, this is completely different and more complex than
            an initial upload
            
            We have two possibilities in this case:
            - We had multiple contigs and are now sending back the reference genome
            - We didn't have a sequence and we're submitting an fna file now
            
            Otherwise what the hell are we doing here? 
            '''
            
            # Case one, sending a reference genome
            message = {'action': 'submit', 'cid': form_data['cid']}
            if 'email_addr' in form_data:
                if settings.DEBUG:
                    print "Received email for notificaion: " + form_data['email_addr']
                message['email'] = form_data['email_addr']
            
            if 'ref_accnum' in form_data and form_data['ref_accnum'] != 'False':
                if settings.DEBUG:
                    print "Received ref_accnum: " + form_data['ref_accnum']
                    
                message['ref_accnum'] = form_data['ref_accnum']
            
            # Case two, we have more data being submitted, this should
            # be an fna file
            elif 'genome_file' in form_data and form_data['genome_file']:
                if settings.DEBUG:
                    print "We received a genome_file in the form data"
                    
                encoded_genome = base64.urlsafe_b64encode( form_data['genome_file'].read() )
                
                message['fna_data'] = encoded_genome
                
            # How did we end up here, we have nothing to do
            else:
                raise("We have a cid but no action to take, error")
            
            try:
                ret = submitter.send_action(message)
            
            except Exception as e:
                if settings.DEBUG:
                    debug_error = ''
                    for arg in e.args:
                        print "{0}\n".format(arg)
                        debug_error += arg
                    raise Exception("Unknown error: " + debug_error)

                raise Exception("Unknown error")
            
            if settings.DEBUG:
                pprint.pprint(ret)
                
            return ret

           
        else:
            kwargs = dict()
            if 'ref_accnum' in form_data and form_data['ref_accnum'] != 'False':
                if settings.DEBUG:
                    print "Received ref_accnum: " + form_data['ref_accnum']

                kwargs['ref_accnum'] = form_data['ref_accnum']

            # We can relax, this is an initial upload
            ret = self.submitUpload(form_data['genome_file'], form_data['format_type'], form_data['genome_name'], form_data['email_addr'], uploader_ip, user_id, **kwargs)
           
            return ret
