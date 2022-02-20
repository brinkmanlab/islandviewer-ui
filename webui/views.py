from django.http import HttpResponse, HttpResponseRedirect, HttpResponseServerError, StreamingHttpResponse, UnreadablePostError
from django.shortcuts import render, get_object_or_404, render_to_response
from django.template import RequestContext
from django.conf import settings
from django import forms
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import last_modified
import json
from webui.models import Analysis, GenomicIsland, GC, CustomGenome, IslandGenes, UploadGenome, Virulence, NameCache, Genes, Replicon, Genomeproject, GIAnalysisTask, Distance, Notification, SiteStatus, STATUS, STATUS_CHOICES, VIRULENCE_FACTORS, MODULES, PICKER_DEFAULTS
from django.core.urlresolvers import reverse
from islandplot import plot
from giparser import fetcher
from uploadparser import uploader
from uploadparser.submitter import send_picker, send_clone, send_notify
from metasched import pipeline, graph
from .forms import UploadGenomeForm
from .utils.formatter import *
import json
import re
import os
import pprint
from collections import OrderedDict
from webui.models import VIRULENCE_FACTORS, VIRULENCE_FACTOR_CATEGORIES
from django.db import OperationalError, connection
from scripts import mauvewrap
import glob
from django.core import serializers
from ratelimit.decorators import ratelimit
from webui.decorators import ratelimit_warning, staff_required

def index(request):
    return render(request, 'index.html')

def showgenomes(request):
    context = {}
    
    params = [STATUS['COMPLETE'], Analysis.MICROBEDB]
    context['analysis'] = Analysis.objects.raw("SELECT Analysis.aid as aid, Analysis.ext_id as ext_id, NameCache.name as name FROM Analysis, NameCache WHERE Analysis.ext_id = NameCache.cid AND Analysis.status = %s AND Analysis.default_analysis = 1 AND Analysis.owner_id = 0 AND Analysis.atype = %s ORDER BY NameCache.name", params)
    
    return render(request, 'selectgenome.html', context)

def showgenomesjson(request):
    context = {}
    
    params = [STATUS['COMPLETE'], Analysis.MICROBEDB]
    context['analysis'] = Analysis.objects.raw("SELECT Analysis.aid as aid, Analysis.ext_id as ext_id, NameCache.name as name FROM Analysis, NameCache WHERE Analysis.ext_id = NameCache.cid AND Analysis.status = %s AND Analysis.default_analysis = 1 AND Analysis.owner_id = 0 AND Analysis.atype = %s ORDER BY NameCache.name", params)
    
    return render(request, "selectgenome.json", context, content_type='text/javascript')

def fetchgenomesjson(request):
        
    genomes = list(NameCache.objects.filter(isvalid=1).values('cid', 'name').all())
    
    data = json.dumps(genomes, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

def results(request, aid):
    # Create the context we're going to add
    # our variables for rending to
    context = {}
    try:
        analysis = Analysis.fetch_by_aid_or_token(aid)
    except Analysis.DoesNotExist:
        context['noanalysis'] = True;

    context['noanalysis'] = False if analysis else True

    if context['noanalysis'] != True:
        context['aid'] = analysis.aid
        context['default_analysis'] = (True if analysis.default_analysis == 1 else False)

        # Check for a security token 
        token = request.GET.get('token') if request.GET.get('token') else aid
        if not analysis.valid_token(token):
            return HttpResponse(status=403)

        # Fetch the genome name and such
        genome = analysis.genome
        context['genomename'] = genome.name
        if genome.contigs > 1:
            ref_accnum = analysis.find_reference_genome()
            ref_genome = Analysis.lookup_genome(ref_accnum)
                
            context['ref_genome'] = ref_genome.name
        
        CHOICES = dict(STATUS_CHOICES)
        context['status'] = CHOICES[analysis.status]
        
        context['token'] = token

        if analysis.status == STATUS['PENDING'] or analysis.status == STATUS['RUNNING']:
            try:    
                context['emails'] = ','.join(Notification.objects.filter(analysis=analysis).values_list('email', flat=True))
            except Exception as e:
                if settings.DEBUG:
                    print e
            pass    


    if request.GET.get('load'):
        context['reload'] = request.GET.get('load')

        context['showtour'] = True
    
    return render(request, 'results.html', context)

def resultsbyaccnum(request, accnum):

    try:
        analysis = get_object_or_404(Analysis, ext_id=accnum, default_analysis=True, atype=Analysis.MICROBEDB)
        return results(request, analysis.aid)
        
    except Exception as e:
        if settings.DEBUG:
            print e
        return HttpResponse(status = 403)

def resultsbyrootaccnum(request, accnum):
    
    try:
        analysis = Analysis.objects.filter(ext_id__startswith = accnum).order_by('-ext_id').all()[0]
        return results(request, analysis.aid)    

    except Exception as e:
        if settings.DEBUG:
            print e
        return HttpResponse(status = 403)

def resultsbyname(request, name):

    try:
        custom_genome = get_object_or_404(CustomGenome, name=name, owner_id=0)
        analysis = get_object_or_404(Analysis, ext_id=custom_genome.cid, owner_id=0)
        return results(request, analysis.aid)
        
    except Exception as e:
        if settings.DEBUG:
            print e
        return HttpResponse(status = 403)
       
@last_modified(Analysis.last_modified)
def circularplotjs(request, aid):
    context = {}
    context['plotName'] = 'circular'
    if(request.GET.get('name')):
        context['plotName'] = request.GET.get('name')
    context['varName'] = ''
    if(request.GET.get('varname')):
        context['varName'] = request.GET.get('varname')
    context['container'] = '#circularchart'
    if(request.GET.get('container')):
        context['container'] = request.GET.get('container')
    if(request.GET.get('skipinit')):
        context['skip_initialize'] = True

    # Fetch the analysis
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['aid'] = aid
    except Analysis.DoesNotExist:
        pass

    # Check for a security token 
    if not analysis.valid_token(request.GET.get('token')):
        return HttpResponse(status=403)

    # Fetch the genome length
    if(analysis.atype == Analysis.CUSTOM):
        genome = CustomGenome.objects.get(pk=analysis.ext_id)
        context['genomesize'] = genome.rep_size
        context['genomename'] = genome.name
        context['ext_id'] = analysis.ext_id
    elif(analysis.atype == Analysis.MICROBEDB):
        (context['genomename'], context['genomesize']) = NameCache.objects.filter(cid=analysis.ext_id).values_list('name', 'rep_size')[0]
        context['ext_id'] = analysis.ext_id

    # Fill in the GIs
    context['gis'] = GenomicIsland.objects.filter(aid_id=aid).order_by('start').all()
    
    json_objs = {'Contig_Gap': [],
                 'Alignments': [],
                 'Islandpick': [],
                 'Integrated': [],
                 'Sigi': [],
                 'Dimob': [],
                 'Islander': []
                 }
    gis = GenomicIsland.objects.filter(aid_id=aid).order_by('start').all()
    for gi in gis:
        rec = {'id': gi.gi, 'start': gi.start, 'end': gi.end, 'name': gi.gi}
        if gi.prediction_method == 'Contig_Gap':
            rec['name'] = 'Contig boundary'
            json_objs['Contig_Gap'].append(rec)
        elif gi.prediction_method == 'Alignments':
            rec['name'] = ('Aligned Contigs' if gi.details == 'aligned' else 'Unaligned Contigs')
            rec['extraclass'] = gi.details if gi.details else ''
            json_objs['Alignments'].append(rec)
        elif gi.prediction_method == 'Islandpick':
            json_objs['Islandpick'].append(rec)
            json_objs['Integrated'].append(rec)
        elif gi.prediction_method == 'Sigi':
            json_objs['Sigi'].append(rec)
            json_objs['Integrated'].append(rec)
        elif gi.prediction_method == 'Dimob':
            json_objs['Dimob'].append(rec)
            json_objs['Integrated'].append(rec)
        elif gi.prediction_method == 'Islander':
            json_objs['Islander'].append(rec)
            json_objs['Integrated'].append(rec)
            
    if json_objs['Contig_Gap'] or json_objs['Alignments']:
        context['contig_controls'] = True
            
    context['Contig_Gap'] = json.dumps(json_objs['Contig_Gap'])
    context['Alignments'] = json.dumps(json_objs['Alignments'])
    context['Integrated'] = json.dumps(json_objs['Integrated'])
    context['Islandpick'] = json.dumps(json_objs['Islandpick'])
    context['Sigi'] = json.dumps(json_objs['Sigi'])
    context['Dimob'] = json.dumps(json_objs['Dimob'])
    context['Islander'] = json.dumps(json_objs['Islander'])
    json_objs = None
    
    # Fetch the GC plot info
    try:
        context['gc'] = GC.objects.get(pk=analysis.ext_id)
    except GC.DoesNotExist:
        pass

    cursor = connection.cursor()
    
    # Fetch the virulence factors
    params = [analysis.ext_id]
    cursor.execute("SELECT @row:=@row+1 AS No, Genes.id, Genes.name, Genes.start, virulence.source, virulence.external_id FROM Genes, virulence_mapped AS virulence, (SELECT @row := 0) r WHERE Genes.ext_id=%s AND Genes.id = virulence.gene_id", params)
    context['vir_factors'] = json.dumps([{'id': vf[1], 'bp': vf[3], 'type': VIRULENCE_FACTOR_CATEGORIES[vf[4]], 'name': vf[4], 'ext_id': vf[5], 'gene': vf[2]} for vf in cursor.fetchall()])

    params = [analysis.ext_id]
#    island_genes = Genes.objects.filter(ext_id=analysis.ext_id).order_by('start').all() 
    
    cursor.execute('SELECT Genes.id, Genes.start, Genes.end, Genes.strand, Genes.name, Genes.gene, Genes.locus FROM Genes WHERE Genes.ext_id = %s ORDER BY Genes.start', params)
    context['genes'] = json.dumps([{'id': gene[0], 'start': gene[1], 'end': gene[2], 'strand': gene[3], 'accnum': gene[4], 'name': (gene[5] if gene[5] else gene[6] if gene[6] else 'Unknown') } for gene in cursor.fetchall()])
    
    return render(request, "circularplot.js", context, content_type='text/javascript')
    

def tablejson(request, aid):
    context = {}
    try:
        analysis = Analysis.objects.get(pk=aid)
    except Analysis.DoesNotExist:
        context['noanalysis'] = True;

    # Check for a security token 
    if not analysis.valid_token(request.GET.get('token')):
        return HttpResponse(status=403)

    context['aid'] = aid
    context['cid'] = analysis.ext_id
    
    # Fill in the GIs
    params = [aid]
    sql = """
    SELECT DISTINCT gi.gi, gi.aid_id, gi.start, gi.end, gi.prediction_method, GROUP_CONCAT( DISTINCT v.type ) AS annotations
    FROM (
      SELECT gi.gi, gi.aid_id, gi.start, gi.end, gi.prediction_method
      FROM GenomicIsland AS gi
      WHERE gi.aid_id = %s
      AND (
        gi.prediction_method =  'Islandpick'
        OR gi.prediction_method =  'Sigi'
        OR gi.prediction_method =  'Dimob'
        OR gi.prediction_method =  'Islander'
      )
    )gi
    LEFT JOIN IslandGenes AS ig ON ig.gi = gi.gi
    LEFT JOIN Genes AS g ON ig.gene_id = g.id
    LEFT JOIN virulence_mapped AS v ON g.name = v.protein_accnum
    GROUP BY gi.gi
    """

    context['gis'] = GenomicIsland.objects.raw(sql, params)
    
    context['gislength'] = sum(1 for result in context['gis'])
    
    return render(request, "table.json", context, content_type='application/json')
    

def search_genes(request, ext_id):
    try:
        t = request.GET.get('term', '')
        q = Q(ext_id = ext_id)
        if request.GET.get('second_ext_id'):
            q |= Q(ext_id = request.GET.get('second_ext_id'))
        genes = Genes.objects.filter(q, Q(product__icontains = t) | Q(name__icontains = t) | Q(locus__icontains = t) | Q(gene__icontains = t))[:30]
        results = []
        for gene in genes:
            gene_json = {}
            gene_json['start'] = gene.start
            gene_json['end'] = gene.end
            gene_json['name'] = gene.name
            gene_json['gene'] = gene.gene if gene.gene else gene.locus
            gene_json['product'] = gene.product
            gene_json['id'] = gene.id
            gene_json['extid'] = gene.ext_id
            results.append(gene_json)
        data = json.dumps(results)
    except OperationalError:
        return HttpResponseServerError('Invalid request')
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def uploadform(request):
    context = {}
    
    try:
        uploadstatus = SiteStatus.objects.all()[0]
        
        if uploadstatus.status != 0:
            context['message'] = uploadstatus.message

            return render(request, 'noupload.html', context)
        
    except Exception as e:
        if settings.DEBUG:
            print "Error getting SiteStatus (a): {}".format(str(e))
    
    if request.method == 'GET':
        form = UploadGenomeForm()
    elif request.method == 'POST':
        form = UploadGenomeForm(request.POST, request.FILES)
        if form.is_valid():
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[-1].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')
            uploadparser = uploader.GenomeParser()
            try:
                ret = uploadparser.submitUpload(request.FILES['genome_file'], form.cleaned_data['format_type'], form.cleaned_data['genome_name'], form.cleaned_data['email_addr'], ip)
            except (ValueError, Exception) as e:
                context['error'] = "Unknown error"
                if settings.DEBUG:
                    print "Unknown error {0}".format(e)
                    for arg in e.args:
                        context['error'] += "<pre>" + "{0}".format(arg) + "</pre>\n"
            else:
                if settings.DEBUG:
                    print "Successful upload, redirect here to analysis"
                # Will be in aid?
                if ret['code'] == 200:
                    m = re.search("\[(\d+)\]", ret['msg'])
                    if m:
                        aid = m.group(1)
                        if settings.DEBUG:
                            print "Found aid: {0}".format(aid)
                            
                        return HttpResponseRedirect(reverse('webui.views.results', kwargs={'aid': aid}))
                    else:
                        context['error'] = "Error parsing results from the server"
                        if settings.DEBUG:
                            context['error'] += "<pre>" + ret['msg'] + "</pre>\n"
                            print "Error str: {0}".format(ret['msg'])
                else:
                    if 'user_error_msg' in ret:
                        context['error'] = ret['user_error_msg']
                    else:
                        # Something really bad happened...
                        context['error'] = "Error submitting genome, we're not even sure what went wrong"

                    if settings.DEBUG:
                        context['error'] += "<pre>Return code: " + str(ret['code']) + "</pre>\n"
                        context['error'] += "<pre>" + ret['msg'] + "</pre>\n"
                        if 'data' in ret and 'code' in ret['data']:
                            context['error'] += "<pre>Error code: " + ret['data']['code'] + "</pre>\n"
                        print "Error str: {0}".format(ret['msg'])
                    
    return render(request,
                  'upload.html',
                  {'form': form})

@csrf_exempt
@ratelimit(group='unauthenticated_upload', rate='5/m', key='ip')
@ratelimit(group='unauthenticated_upload', rate='20/h', key='ip')
@ratelimit_warning
def uploadcustomajax(request, **kwargs):

    return _uploadcustomajax(request, **kwargs)

def _uploadcustomajax(request, **kwargs):
    """
     Helper function so rate limiting only applies to the ajax call and not when
     we call uploadcustomajax via the REST endpoint
    """
    
    context = {}
    
    if settings.DEBUG:
        pprint.pprint(request.POST)

    try:
        if request.method == 'POST':
            form = UploadGenomeForm(request.POST, request.FILES)
            if form.is_valid():
                if settings.DEBUG:
                    print "valid"
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip = x_forwarded_for.split(',')[-1].strip()
                else:
                    ip = request.META.get('REMOTE_ADDR')
                uploadparser = uploader.GenomeParser()

                try:
                    if request.user.is_authenticated():
                        user_id = request.user.id
                    else:
                        # See if we've been passed a userid from the caller (ie. rest upload view), otherwise, None
                        user_id = getattr(kwargs, 'userid', None)
                    ret = uploadparser.submitCustom(form.cleaned_data, ip, user_id)
                except (ValueError, Exception) as e:
                    context['error'] = "Unknown error"
                    if settings.DEBUG:
                        print "Unknown error {0}".format(e)
                        for arg in e.args:
                            context['error'] += "<pre>" + "{0}".format(arg) + "</pre>\n"

                        context['status'] = 500
                else:
                    # We received a result from the backend
                    if settings.DEBUG:
                        print "Successful upload, redirect here to analysis"
                    # Will be in aid?
                    if ret['code'] == 200:
                        m = re.search("\[(\d+)\]", ret['msg'])
                        if m:
                            aid = m.group(1)
                            if settings.DEBUG:
                                print "Found aid: {0}".format(aid)

                            context['status'] = 200
                            context['aid'] = aid
                            if 'data' in ret and 'token' in ret['data']:
                                if settings.DEBUG:
                                    print "Found token: " + ret['data']['token']
                                context['token'] = ret['data']['token']

                        else:
                            context['error'] = "Error parsing results from the server"
                            if settings.DEBUG:
                                context['error'] += "<pre>" + ret['msg'] + "</pre>\n"
                                print "Error str: {0}".format(ret['msg'])

                            context['status'] = 500

                    else:
                        # Just because we received a 500 doesn't mean this is fatal,
                        # it just means something went wrong in processing and perhaps
                        # there's corrective action the user can take
                        if 'user_error_msg' in ret:
                            context['error'] = ret['user_error_msg']
                        else:
                            # Something really bad happened...
                            context['error'] = "Error submitting genome, we're not even sure what went wrong"

                        if settings.DEBUG:
                            context['error'] += "<pre>Return code: " + str(ret['code']) + "</pre>\n"
                            context['error'] += "<pre>" + ret['msg'] + "</pre>\n"
                            if 'data' in ret and 'code' in ret['data']:
                                context['error'] += "<pre>Error code: " + ret['data']['code'] + "</pre>\n"
                            print "Error str: {0}".format(ret['msg'])

                        # It might not be an error, see if there's a cid and code
                        if 'data' in ret:
                            context.update( ret['data'] )

                        if 'code' in ret:
                            context['status'] = ret['code']
                        else:
                            context['status'] = 500
            else:
                # If we've gotten here, someone is doing something naughty, screw'em
                if settings.DEBUG:
                    print form.errors, 'here1'
                    print form.non_field_errors(), 'here2'
                    field_errors = [(field.label, field.errors) for field in form]
                    print field_errors, 'here3'

        else:
            return HttpResponse(status=400)
    except UnreadablePostError:
        return HttpResponseServerError('Missing POST data')
 
    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")


def uploadredirect(request, upload_id):
    context = {}

    upload = get_object_or_404(UploadGenome, pk=upload_id)
    
    if upload.aid == 0:
        return render(request, 'uploadredirect.html')
    else:
        return HttpResponseRedirect(reverse('webui.views.results', kwargs={'aid': upload.aid}))

@staff_required
def runstatus(request):
    context = {}

    context['analysis'] = Analysis.objects.select_related().all()
    
    return render(request, 'status.html', context)
    


@staff_required
def runstatusjson(request):
    context = {}

    context['sEcho'] = 1
    if(request.GET.get('sEcho')):
        sEcho = request.GET.get('sEcho')
        if not sEcho.isdigit():
            return HttpResponse(status=400)

        context['sEcho'] = int(sEcho)

    startAt = 0
    if(request.GET.get('iDisplayStart')):
        startAt = request.GET.get('iDisplayStart')
        try:
            int(startAt)
        except ValueError:
            return HttpResponse(status=400)

        startAt = int(startAt)

    toShow = 30
    if(request.GET.get('iDisplayLength')):
        try:
            int(request.GET.get('iDisplayLength'))
        except ValueError:
            return HttpResponse(status=400)

        iDisplayLength = int(request.GET.get('iDisplayLength'))
        if iDisplayLength > 0:
            toShow = iDisplayLength

        toShow = int(toShow)

    endAt = startAt + toShow

    analysis = Analysis.objects.select_related().order_by('-aid').all()

    context['records'] = len(analysis)

    context['analysis'] = analysis[startAt:endAt]
    
    return render(request, 'status.json', context)

@staff_required
def runstatusdetailsjson(request, aid):
    context = {}
    
    analysis = Analysis.objects.select_related().get(pk=aid)
    CHOICES = dict(STATUS_CHOICES)

    context['aid'] = analysis.aid

    # Fetch the genome name and such
    if(analysis.atype == Analysis.CUSTOM):
        genome = CustomGenome.objects.get(pk=analysis.ext_id)
        context['genomename'] = genome.name
    elif(analysis.atype == Analysis.MICROBEDB):
        context['genomename'] = NameCache.objects.get(cid=analysis.ext_id).name
    
    context['tasks'] = {}
    context['taskcount'] = {}
    for method in analysis.tasks.all():
        context['tasks'][method.prediction_method] = CHOICES[method.status]
        try:
            context['taskcount'][method.prediction_method] = GenomicIsland.objects.filter(aid=analysis, prediction_method=method.prediction_method).count()
        except Exception as e:
            if settings.DEBUG:
                print str(e)
            pass
    
    try:
        context['emails'] = ','.join(Notification.objects.filter(analysis=analysis).values_list('email', flat=True))
    except Exception as e:
        if settings.DEBUG:
            print e
        pass    
    
    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

@csrf_exempt
def add_notify(request, aid):
    context = {}
    
    if request.method == 'POST':

        try:
            analysis = Analysis.objects.get(pk=aid)
        except Exception as e:
            if settings.DEBUG:
                print e
                
            return HttpResponse(status=400)

        if 'email' in request.POST:
            email = request.POST.get('email')

            try: 
                f = forms.EmailField()
                f.clean(email)
                
                notify_ret = send_notify(aid, email)
                
                if 'code' in notify_ret and notify_ret['code'] == 200:
                    context['status'] = 'success'

                else:
                    context['status'] = 'failed'
                    context['msg'] = notify_ret['msg']
                    if settings.DEBUG:
                        context['debug'] = notify_ret
                        
                 
            
            except Exception as e:
                if settings.DEBUG:
                    print e
                return HttpResponse(status=500)
        else:
            if settings.DEBUG:
                print "No email"
            return HttpResponse(status=500)


    else:
        return HttpResponse(status=500)

    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

@staff_required
def restartmodule(request, aid):
    context = {}
    
    if(request.GET.get('module') and request.GET.get('module') in MODULES):
        module = request.GET.get('module')
    else:
        return HttpResponse(status=400)

    clone_kwargs = { 'action': 'rerun', 'args': { 'modules': { module: { 'args': {  } } } } }

    clone_ret = send_clone(aid, **clone_kwargs)

    if 'code' in clone_ret and clone_ret['code'] == 200:
        if settings.DEBUG:
            print "Job submitted, new aid: " + clone_ret['data']
        
        context['status'] = 'success'
        context['aid'] = clone_ret['data']                

    else:
        context['status'] = 'failed'
        context['msg'] = clone_ret['msg']
        if settings.DEBUG:
            context['debug'] = clone_ret

    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

@staff_required
def logsmodule(request, aid):
    context = {}
    
    if(request.GET.get('module') and (request.GET.get('module') in MODULES or request.GET.get('module') == 'All')):
        module = request.GET.get('module')
    else:
        return HttpResponse(status=400)
    
    # Build the path for the analysis log
    if module == 'All':
        filename = os.path.join(settings.ANALYSIS_PATH, aid, 'analysis.log')
    else:
        filename = os.path.join(settings.ANALYSIS_PATH, aid, module, 'analysis.log')
    
    if settings.DEBUG:
        print filename
        context['filename'] = filename

    if not os.path.isfile(filename):
        context['status'] = 'failed'
        context['msg'] = "File not found"

    elif(request.GET.get('show')):            
        fsock = open(filename,"r")
    
        response = StreamingHttpResponse(fsock, content_type='text/plain')
        
        return response

    else:
        context['status'] = 'success'
        
    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")
    
def graphanalysis(request, aid):
    context = {}
    context['aid'] = aid
    
    return render(request, 'graphanalysis.html', context)

def graphanalysisjs(request, aid):
    context = {}
    grapher = graph.Grapher()

    # Fetch the pipeline's structure
    pipeline_reader = pipeline.Parser()
    pipeline_data = pipeline_reader.read(settings.PIPELINE)

    context['json_str'] = grapher.makeGraph(aid, pipeline_data);
    
    return render(request, 'graphanalysis.js', context, content_type='text/javascript')

def fetchislands(request):
    context = {}
    if request.GET.get('aid'):        
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        context['aid'] = aid
    elif request.GET.get('gi'):
        gi = request.GET.get('gi')
        if not gi.isdigit():
            return HttpResponse(status=400)
        girec = get_object_or_404(GenomicIsland, pk=gi)
        aid = girec.aid_id
        context['gi'] = str(gi)
        context['aid'] = aid
    else:
        return HttpResponse(status=400)
    
    analysis = get_object_or_404(Analysis, pk=aid)
    if not analysis.valid_token(request.GET.get('token')):
        return HttpResponse(status=403)

    try:
        p = fetcher.GenbankParser(aid)
    except ValueError as e:
        response = HttpResponseServerError(reason='Unable to parse Genbank')
        response.content = "<h1>Unable to parse Genbank</h1><pre>" + e.message + "</pre>"
        return response
    recs = p.fetchRecords()
    
    islands = {}
    dna = {}
    if 'gi' in context:
        islands.update(recs[long(gi)])
    else:
        if settings.DEBUG:
            print type(recs)
        for islandid in recs:
            islands.update(recs[islandid])
            
    context['islands'] = sorted(islands.iteritems(), key= lambda (k,v): int(v['start']))
    context['fastaseq'] = dna

    return render(request, "islands_by_gi.html", context)

def genesjson(request, gi_id):
    context = {}
    
    girec = get_object_or_404(GenomicIsland, pk=gi_id)
    context['gi'] = gi_id
    context['startbp'] = girec.start
    context['endbp'] = girec.end
    analysis = girec.aid
    context['aid'] = analysis.aid
    context['method'] = girec.prediction_method
    
    params = [gi_id]
    context['genes'] = Genes.objects.raw("select Genes.* FROM Genes, IslandGenes WHERE IslandGenes.gi = %s AND Genes.id = IslandGenes.gene_id ORDER BY Genes.start", params)

    return render(request, "genes.json", context, content_type='application/json')

def genesbybpjson(request):
    context = {}
    
    if not request.method == 'GET':
        return HttpResponse(status = 403)
    
    if request.GET.get('ext_id'):
        ext_id = request.GET.get('ext_id')
    else:
        return HttpResponse(status = 403)

    if request.GET.get('aid'):
        aid = request.GET.get('aid')
    else:
        return HttpResponse(status = 403)
    
    if request.GET.get('start') and request.GET.get('start').isdigit():
        start = request.GET.get('start')
    else:
        return HttpResponse(status = 403)

    if request.GET.get('end') and request.GET.get('end').isdigit():
        end = request.GET.get('end')
    else:
        return HttpResponse(status = 403)
    
    params = [aid, ext_id, start, end]
    context['genes'] = Genes.objects.raw("SELECT DISTINCT g.id, g.start, g.end, g.name, g.gene, g.product, g.locus, GROUP_CONCAT( ig.gi ) AS gi , GROUP_CONCAT( DISTINCT gi.prediction_method ) AS method, GROUP_CONCAT( DISTINCT v.source ) AS virulence FROM Genes AS g LEFT JOIN IslandGenes AS ig ON g.id = ig.gene_id LEFT JOIN GenomicIsland AS gi ON ig.gi = gi.gi AND gi.aid_id = %s LEFT JOIN virulence_mapped AS v ON g.id = v.gene_id WHERE g.ext_id = %s AND g.end >=%s AND g.start <=%s GROUP BY g.id", params)

    return render(request, "genesbybp.json", context, content_type='application/json')


def islandpick_select_genomes(request, aid):
    context = {}

    try:
        uploadstatus = SiteStatus.objects.all()[0]
        
        if uploadstatus.status != 0:
            context['message'] = uploadstatus.message
            context['nouploads'] = True
        
    except Exception as e:
        if settings.DEBUG:
            print "Error getting SiteStatus (b): {}".format(str(e))
    
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['aid'] = analysis.aid

        # Fetch the genome name and such
        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            context['genomename'] = genome.name
        elif(analysis.atype == Analysis.MICROBEDB):
            context['genomename'] = NameCache.objects.get(cid=analysis.ext_id).name

        context['related_analysis'] = Analysis.objects.filter(ext_id=analysis.ext_id, owner_id=0).all()
        

    except:
        pass

    return render(request, "islandpick_select_genomes.html", context)


@csrf_exempt
def islandpick_genomes_json(request, aid, **kwargs):

    # Were we given parameters?
    for p in ['min_cutoff', 'max_cutoff', 'max_dist_single_cutoff', 'max_compare_cutoff', 'min_gi_size', 'reselect']:
        if not request.GET.get(p):
            continue
        try:
            kwargs[p] = float(request.GET.get(p))
        except Exception as e:
            if settings.DEBUG:
                print "Sent a bad value for {}, ignoring: {}".format(p, str(e))
            pass

    try:
        picked_genomes = []
        if request.method == 'POST':
            for name in request.POST:
                picked_genomes.append(name)

        results = islandpick_genomes(aid, picked=picked_genomes, **kwargs)
        if isinstance(results, HttpResponse):
            return results
        
    except Exception as e:
        if settings.DEBUG:
            print str(e)
        return HttpResponse(status = 403)

    data = json.dumps(results, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

def islandpick_genomes(aid, picked=None, reselect=False, **kwargs):
    context = {}
    
    try:
        analysis = Analysis.objects.get(pk=aid)
        context['accnum'] = analysis.ext_id
        context['default_analysis'] = (True if analysis.default_analysis == 1 else False)
    except Analysis.DoesNotExist:
        if settings.DEBUG:
            print "Can't fetch analysis"
        return HttpResponse(status = 403)

    selected = {}
    try:
        iptask = GIAnalysisTask.objects.get(aid=aid, prediction_method='Islandpick')
        
        parameters = json.loads(iptask.parameters)
        context['parameters'] = parameters

        # Get previously used parameters, if they exist
        for p in ['min_cutoff', 'max_cutoff']:
            if p in parameters and p not in kwargs:
                kwargs[p] = float(parameters[p])

    except Exception as e:
        if settings.DEBUG:
            print e
        raise Exception("Can't find analysis task")

    if 'comparison_genomes' in parameters:
        selected = {x: True for x in parameters['comparison_genomes'].split()}
        kwargs.update({'extra_genomes': selected})
    else:
        context['nogenomesselected'] = True
        
    genomes = Distance.find_genomes(analysis.ext_id, **kwargs)

    if not picked:

        try:

            # Now get all the names
            ext_ids = [g for g,d in genomes]
            cache_names = NameCache.objects.filter(cid__in=ext_ids).values('cid', 'name')
            cache_names = {x['cid']:x['name'] for x in cache_names}
            cids = [int(x) for x in ext_ids if x.isdigit()]
            custom_names = CustomGenome.objects.filter(cid__in=cids).values('cid', 'name')
            custom_names = {x['cid']:x['name'] for x in custom_names}

        except Exception as e:
            if settings.DEBUG:
                print str(e)
            pass

        genome_list = OrderedDict()

        # We need the genomes to display in order
        for g,dist in sorted(genomes, key=lambda genome: genome[1]):
            # We don't want custom genomes, so skip anything without
            # a namecache entry for now
            if g not in cache_names:
                continue
            genome_list.update({g: {'dist': "%0.3f" % dist,
                                    'used': (True if g in selected else False),
                                    'picked' : (True if g in selected and not reselect else False),
                                    'name': (cache_names[g] if g in cache_names else custom_names[g] if g in custom_names else "Unknown" )
                                    }
                                })

        if reselect:
            try:
                if settings.DEBUG:
                    print "Sending to picker: {}".format(analysis.ext_id)
                    pprint.pprint(kwargs)
                # If we're re-selecting the candidates, make the call to the backend
                picker = send_picker(analysis.ext_id, **kwargs)

                if settings.DEBUG:
                    print "From picker"
                    pprint.pprint(picker)

                if 'code' in picker and picker['code'] == 200:
                    for acc in picker['data']:
                        if "picked" in picker['data'][acc] and acc in genome_list:
                            genome_list[acc]["picked"] = 'true'
                    
                context['picker'] = picker
            except Exception as e:
                if settings.DEBUG:
                    print "Exception: " + str(e)
                context['picker'] = {'code': 500}


        context['genomes'] = genome_list
        context['status'] = "OK"            
        
        if settings.DEBUG:
            pprint.pprint(context)
        return context

    else:
        try:
        
            #print request.GET.get('min_gi_size')
            accnums = []
            min_gi_size = int(getattr(kwargs, 'min_gi_size', PICKER_DEFAULTS['min_gi_size']))
            for name in picked:
                #print name, request.POST[name]
                if name not in (x[0] for x in genomes):
                    if settings.DEBUG:
                        print "Error, " + name + " not in genomes set"
                    raise Exception("Error, requested genome isn't in the allowed set")
                accnums.append(name)

            clone_kwargs = { 'args': { 'modules': { 'Islandpick': { 'args': { 'comparison_genomes':  ' '.join(accnums), 'MIN_GI_SIZE': min_gi_size } } } } }

            # Check if we've run these settings before, if so, just redirect to that
            match_aid = Analysis.find_islandpick(analysis.ext_id, accnums, min_gi_size)
            if match_aid:
                context['status'] = 'success'
                context['aid'], token = match_aid
                if token:
                    context['token'] = token
            
            else:
                if analysis.is_precomputed:
                    user_id = 1
                else:
                    user_id = analysis.owner_id

                clone_ret = send_clone(aid, user_id=user_id, **clone_kwargs)
            
                if 'code' in clone_ret and clone_ret['code'] == 200:
                    if settings.DEBUG:
                        print "Job submitted, new aid: " + clone_ret['data']
                    
                    context['status'] = 'success'
                    aid = clone_ret['data']
                    context['aid'] = aid
                    try:
                        new_analysis = Analysis.objects.get(pk=aid)
                        if new_analysis.token:
                            context['token'] = new_analysis.token
                    except:
                        pass               
        
        except Exception as e:
            if settings.DEBUG:
                print "Error in post"
                print str(e)
            return HttpResponse(status = 403)

        if settings.DEBUG:
            pprint.pprint(context)
        return context

def downloadCoordinates(request):
    
    if request.GET.get('aid'):
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        analysis = Analysis.objects.get(pk=aid)

        # Check for a security token 
        if not analysis.valid_token(request.GET.get('token')):
            return HttpResponse(status=403)


        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            filename = genome.name
            filename = ''.join(e for e in filename if e.isalnum())
        elif(analysis.atype == Analysis.MICROBEDB):
            filename = analysis.ext_id
    else:
        return HttpResponse(status=400)
        
    if request.GET.get('format'):
        format = request.GET.get('format')
        if format not in downloadformats:
            return HttpResponse(status=400)
        extension = downloadextensions[format]
    else:
        return HttpResponse(status=400)

    if request.GET.getlist('methods'):
        if settings.DEBUG:
            pprint.pprint(request.GET.getlist('methods'))
        methods = request.GET.getlist('methods')
        if settings.DEBUG:
            pprint.pprint(methods)
    else:
        methods = ['integrated']

    params = [aid]   
    islandset = Genes.objects.raw("SELECT G.id, GI.gi AS gi, GI.start AS island_start, GI.end AS island_end, GI.prediction_method, G.ext_id, G.start AS gene_start, G.end AS gene_end, G.strand, G.name, G.gene, G.product, G.locus, GROUP_CONCAT( DISTINCT V.source ) AS virulence FROM Genes AS G JOIN IslandGenes AS IG ON G.id = IG.gene_id JOIN GenomicIsland AS GI ON GI.gi = IG.gi LEFT JOIN virulence_mapped AS V ON G.name = V.protein_accnum WHERE GI.aid_id = %s GROUP BY IG.id ORDER BY GI.start, GI.prediction_method", params)
    if settings.DEBUG:
        pprint.pprint(islandset)

    try:
        response = downloadformats[format](islandset, None,methods, filename + "." + extension)
    except ValueError as e:
        response = HttpResponseServerError(reason='Unable to parse Genbank')
        response.content = "<h1>Unable to write " + format + "</h1><pre>" + e.message + "</pre>"
        return response

    return response

def downloadAnnotations(request):

    if request.GET.get('aid'):
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        analysis = Analysis.objects.get(pk=aid)

        # Check for a security token 
        if not analysis.valid_token(request.GET.get('token')):
            return HttpResponse(status=403)

        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            filename = genome.name
            filename = ''.join(e for e in filename if e.isalnum())
        elif(analysis.atype == Analysis.MICROBEDB):
            filename = analysis.ext_id

    else:
        return HttpResponse(status=400)
        
    if request.GET.get('format'):
        format = request.GET.get('format')
        if format not in downloadformats:
            return HttpResponse(status=400)
        extension = downloadextensions[format]
    else:
        return HttpResponse(status=400)

    params = [analysis.ext_id]
    annotations = Genes.objects.raw("SELECT G.id, G.name, G.start, G.end, V.external_id, V.source FROM Genes AS G JOIN virulence_mapped AS V ON G.name = V.protein_accnum WHERE G.ext_id = %s ORDER BY V.source", params)

    try:
        response = annotationformats[format](annotations, filename + '_annotations' + '.' + extension)
    except ValueError as e:
        response = HttpResponseServerError(reason='Unable to parse Genbank')
        response.content = "<h1>Unable to write " + format + "</h1><pre>" + e.message + "</pre>"
        return response

    return response

def downloadSequences(request):
    
    if request.GET.get('aid'):
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        analysis = Analysis.objects.get(pk=aid)
        try:
            p = fetcher.GenbankParser(aid)
        except ValueError as e:
            response = HttpResponseServerError(reason='Unable to parse Genbank')
            response.content = "<h1>Unable to parse Genbank</h1><pre>" + e.message + "</pre>"
            return response

        # Check for a security token 
        if not analysis.valid_token(request.GET.get('token')):
            return HttpResponse(status=403)

        if(analysis.atype == Analysis.CUSTOM):
            genome = CustomGenome.objects.get(pk=analysis.ext_id)
            filename = genome.name
            filename = ''.join(e for e in filename if e.isalnum())
        elif(analysis.atype == Analysis.MICROBEDB):
            filename = analysis.ext_id
    else:
        return HttpResponse(status=400)
        
    if request.GET.get('format'):
        format = request.GET.get('format')
        if format not in downloadformats:
            return HttpResponse(status=400)
        extension = downloadextensions[format]
    else:
        return HttpResponse(status=400)

    if request.GET.getlist('methods'):
        if settings.DEBUG:
            pprint.pprint(request.GET.getlist('methods'))
        methods = request.GET.getlist('methods')
        if settings.DEBUG:
            pprint.pprint(methods)
    else:
        methods = ['integrated']

    params = [aid] 
    if(format == 'genbank'):
        islandset = GenomicIsland.objects.filter(aid_id=aid).order_by('start').all()
    else:
        islandset = Genes.objects.raw("SELECT G.id, GI.gi AS gi, GI.start AS island_start, GI.end AS island_end, GI.prediction_method, G.ext_id, G.start AS gene_start, G.end AS gene_end, G.strand, G.name, G.gene, G.product, G.locus, GROUP_CONCAT( DISTINCT V.source ) AS virulence FROM Genes AS G JOIN IslandGenes AS IG ON G.id = IG.gene_id JOIN GenomicIsland AS GI ON GI.gi = IG.gi LEFT JOIN virulence_mapped AS V ON G.name = V.protein_accnum WHERE GI.aid_id = %s GROUP BY IG.id ORDER BY GI.start, GI.prediction_method", params)

    try:
        response = downloadformats[format](islandset, p, methods, filename + "." + extension)
    except ValueError as e:
        response = HttpResponseServerError(reason='Unable to parse Genbank')
        response.content = "<h1>Unable to write " + format + "</h1><pre>" + e.message + "</pre>"
        return response

    return response

    
    
def fetchislandsfasta(request):
    context = {}
    gi = 0
    if request.GET.get('aid'):        
        aid = request.GET.get('aid')
        if not aid.isdigit():
            return HttpResponse(status=400)
        analysis = get_object_or_404(Analysis, pk=aid)
        filename = analysis.ext_id
    elif request.GET.get('gi'):
        gi = request.GET.get('gi')
        if not gi.isdigit():
            return HttpResponse(status=400)
        girec = get_object_or_404(GenomicIsland, pk=gi)
        aid = girec.aid_id
        gi = str(gi)
        aid = aid
        analysis = get_object_or_404(Analysis, pk=aid)
        filename = str(girec.start) + '_' + str(girec.end)
        rangestr = str(girec.start) + '..' + str(girec.end)
    else:
        return HttpResponse(status=400)
        # Check for a security token 

    if not analysis.valid_token(request.GET.get('token')):
        return HttpResponse(status=403)
    
    seqtype = 'protein'
    if request.GET.get('seq'):
        seqtype = request.GET.get('seq')
        if seqtype not in ('protein', 'nuc', 'island'):
            return HttpResponse(status=400)

    try:
        p = fetcher.GenbankParser(aid)
    except ValueError as e:
        response = HttpResponseServerError(reason='Unable to parse Genbank')
        response.content = "<h1>Unable to parse Genbank</h1><pre>" + e.message + "</pre>"
        return response

    if seqtype == 'island':
        if gi:
            fasta = p.generateIslandFasta(gi, rangestr)
        else:
            return HttpResponse(status=400)
    else:
        fasta = p.generateFasta(gi=gi, seqtype=seqtype, show_methods = True)
    
    response = HttpResponse(content_type='text/plain')
    response['Content-Disposition'] = "attachment; filename=\"gi_{0}.txt\"".format(filename)
    response.write(fasta)
    return response

def getMauveFile(request):
    firstgenomeextid = request.GET.get('firstgenomeextid')
    secondgenomeextid = request.GET.get('secondgenomeextid')

    firstgenomeextid = firstgenomeextid.split('.')[0]
    secondgenomeextid = secondgenomeextid.split('.')[0]

    firstReplicon = Replicon.objects.using('microbedb').filter(rep_accnum__contains=firstgenomeextid)[0]
    secondReplicon = Replicon.objects.using('microbedb').filter(rep_accnum__contains=secondgenomeextid)[0]

    firstGenomeProject = Genomeproject.objects.using('microbedb').get(gpv_id__exact=firstReplicon.gpv_id)
    secondGenomeProject = Genomeproject.objects.using('microbedb').get(gpv_id__exact=secondReplicon.gpv_id)

    firstGbk = glob.glob(firstGenomeProject.gpv_directory+"/*"+".gbk")[0]
    secondGbk = glob.glob(secondGenomeProject.gpv_directory+"/*"+".gbk")[0]

    mauveOutputPath = mauvewrap.getMauveResults(firstGbk,secondGbk)

    with open(mauveOutputPath,'r') as f:
        data = f.read()

    return HttpResponse(data)

def about(request):
    
    return render(request, "about.html")

def download(request):
    
    return render(request, "download.html")
        
def resources(request):
    
    return render(request, "resources.html")

def contactus(request):
    
    return render(request, "contactus.html")

def faq(request):
    
    return render(request, "faq.html")

def acknowledgements(request):
    
    return render(request, "acknowledgements.html")

def islandpick(request):
    
    return render(request, "islandpick.html")

def http_api(request):
    
    return render(request, "http_api.html")

