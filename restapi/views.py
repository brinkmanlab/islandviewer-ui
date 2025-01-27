from django.http import HttpResponse, HttpResponseServerError
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import F

import json
from ratelimit.decorators import ratelimit

from webui.models import Analysis, CustomGenome, GenomicIsland, NameCache, Notification, STATUS_CHOICES, GI_MODULES, PICKER_DEFAULTS
from webui.views import _uploadcustomajax, islandpick_genomes
from webui.decorators import auth_token, ratelimit_warning, scrub_picker, parameter_parser
from webui.utils import formatter
from giparser import fetcher
from uploadparser.submitter import send_clone

'''
Rate limits for authenticated and unauthenticated users
'''
minute_rate = lambda group, request: '10/m' if request.user.is_authenticated() else '10/min'
hour_rate = lambda group, request: '120/h' if request.user.is_authenticated() else '120/hour'

submission_minute_rate = lambda group, request: '2/m' if request.user.is_authenticated() else '2/m'
submission_hour_rate = lambda group, request: '30/h' if request.user.is_authenticated() else '30/h'
submission_day_rate = lambda group, request: '200/d' if request.user.is_authenticated() else '200/d'

@auth_token
@ratelimit(group='rest', key='user', rate=minute_rate)
@ratelimit(group='rest', key='user', rate=hour_rate)
@ratelimit_warning
def user_jobs(request, **kwargs):

    user = request.user
    analysis = Analysis.objects.filter(owner_id=user.id).order_by('-aid')
    
    analysis_set = []
    CHOICES = dict(STATUS_CHOICES)

    for a in analysis:
        """A big assumption! That it's a custom genome.
           Fetching genome names (done multiple places) should be
           abstracted out at some point."""
        genome = CustomGenome.objects.get(pk=a.ext_id)

        analysis_set.append({'token': a.token,
                             'results': request.build_absolute_uri( reverse('results', kwargs={'aid': a.token}) ),
                             'genome_name': genome.name,
                             'status': CHOICES[a.status],
                             })

    data = json.dumps(analysis_set, indent=4, sort_keys=False)

    return HttpResponse(data, content_type="application/json")

@auth_token(allow_anonymous=True)
@ratelimit(group='rest', key='user_or_ip', rate=minute_rate)
@ratelimit(group='rest', key='user_or_ip', rate=hour_rate)
@ratelimit_warning
def user_job(request, aid, **kwargs):
    user = request.user
    analysis = Analysis.fetch_by_aid_or_token(aid)

    if not analysis:
        return HttpResponse(status = 403)

    CHOICES = dict(STATUS_CHOICES)
    context = {}

    if not analysis.is_owner_or_anonymous(user.id):
        return HttpResponse(status=401)
    
    context['token'] = analysis.token
    context['status'] = CHOICES[analysis.status]
    context['results'] = request.build_absolute_uri( reverse('results', kwargs={'aid': analysis.token}) )
    
    # Fetch the genome name and such
    if(analysis.atype == Analysis.CUSTOM):
        genome = CustomGenome.objects.get(pk=analysis.ext_id)
        context['genome_name'] = genome.name
    elif(analysis.atype == Analysis.MICROBEDB):
        context['genome_name'] = NameCache.objects.get(cid=analysis.ext_id).name
    
    context['tasks'] = {}
    context['taskcount'] = {}
    for method in analysis.tasks.all():
        context['tasks'][method.prediction_method] = CHOICES[method.status]

        if method.prediction_method not in GI_MODULES:
            continue
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

@auth_token(allow_anonymous=True)
@ratelimit(group='rest', key='user_or_ip', rate=minute_rate)
@ratelimit(group='rest', key='user_or_ip', rate=hour_rate)
@ratelimit_warning
@scrub_picker
def user_job_islandpick(request, aid, **kwargs):
    """
    Show Islandpick parameters that were used
    """

    user = request.user
    analysis = Analysis.fetch_by_aid_or_token(aid)

    if not analysis:
        return HttpResponse(status = 403)

    if not analysis.is_owner_or_anonymous(user.id):
        return HttpResponse(status=401)

    try:
        results = islandpick_genomes(analysis.aid)
        
    except Exception as e:
        if settings.DEBUG:
            print str(e)
        return HttpResponse(status = 403)

    return results

@parameter_parser
@csrf_exempt
@auth_token(allow_anonymous=True)
@ratelimit(group='rest', key='user_or_ip', rate=minute_rate)
@ratelimit(group='rest', key='user_or_ip', rate=hour_rate)
@ratelimit_warning
@scrub_picker(remove_keys=['genomes'])
def user_job_picker(request, aid, **kwargs):
    """
    Run genome picker with new parameters to select new
    candidate genomes.
    """
    user = request.user
    analysis = Analysis.fetch_by_aid_or_token(aid)

    if not analysis:
        return HttpResponse(status = 403)

    if not analysis.is_owner_or_anonymous(user.id):
        return HttpResponse(status=401)

    # Were we given parameters?
    for p in ['min_cutoff', 'max_cutoff', 'max_dist_single_cutoff', 'max_compare_cutoff', 'min_gi_size']:
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

        results = islandpick_genomes(analysis.aid, reselect=True, **kwargs)
        
    except Exception as e:
        if settings.DEBUG:
            print str(e)
        return HttpResponse(status = 403)

    return results

@parameter_parser(allow_methods='POST')
@csrf_exempt
@auth_token(allow_anonymous=True)
@ratelimit(group='rest_submit', key='user_or_ip', rate=submission_minute_rate)
@ratelimit(group='rest_submit', key='user_or_ip', rate=submission_hour_rate)
@ratelimit(group='rest_submit', key='user_or_ip', rate=submission_day_rate)
@ratelimit_warning
def user_job_islandpick_rerun(request, aid, **kwargs):
    """
    Submit an Islandpick job with new parameters.
    """
    context = {}
    user = request.user
    analysis = Analysis.fetch_by_aid_or_token(aid)

    if not analysis:
        return HttpResponse(status = 403)

    if settings.DEBUG:
        import pprint
        pprint.pprint(kwargs)

    if not (analysis.is_owner_or_anonymous(user.id) and analysis.is_complete):
        if settings.DEBUG:
            print "uid used is {}".format(user.id)
            print "analysis user is {}".format(analysis.owner_id)
            print "analysis status: {}".format(analysis.status)
        return HttpResponse(status=401)

    try:        
        accnums = []
        min_gi_size = int(kwargs.get('min_gi_size', PICKER_DEFAULTS['min_gi_size']))
        if 'genomes' not in kwargs:
            return HttpResponse(status=403)

        for accnum in kwargs['genomes']:
            print "looking for {}".format(accnum)
            genome = Analysis.lookup_genome(accnum)
            
            if genome.is_system_owned or (genome.is_owner_or_anonymous(user.id) and genome.isvalid):
                accnums.append(accnum)
            else:
                if settings.DEBUG:
                    print "Error, " + accnum + " not in genomes set"
                    raise Exception("Error, requested genome isn't valid or allowed")

        clone_kwargs = { 'args': { 'modules': { 'Islandpick': { 'args': { 'comparison_genomes':  ' '.join(accnums), 'MIN_GI_SIZE': min_gi_size } } } } }

            # Check if we've run these settings before, if so, just redirect to that
        match_aid = Analysis.find_islandpick(analysis.ext_id, accnums, min_gi_size)
        if match_aid:
            new_analysis = Analysis.objects.get(pk=match_aid[0])
            if new_analysis.is_owner_or_anonymous(user.id):
                context['status'] = 'success'
                new_aid, token = match_aid
                if token:
                    context['token'] = token
                else:
                    context['aid'] = new_aid
            
        else:
            if analysis.is_precomputed:
                user_id = 1
            else:
                user_id = analysis.owner_id

            clone_ret = send_clone(analysis.aid, user_id=user_id, **clone_kwargs)
            
            if 'code' in clone_ret and clone_ret['code'] == 200:
                if settings.DEBUG:
                    print "Job submitted, new aid: " + clone_ret['data']
                    
                context['status'] = 'success'
                aid = int(clone_ret['data'])
                context['aid'] = aid
                try:
                    new_analysis = Analysis.objects.get(pk=aid)
                    if new_analysis.token:
                        context['token'] = new_analysis.token
                except Exception as e:
                    if settings.DEBUG:
                        print "Can't find new analysis {}, that's bad bad bad".format(aid)
                        print str(e)
                    pass               
        
    except Exception as e:
        if settings.DEBUG:
            print "Error in post"
            print str(e)
        return HttpResponse(status = 403)

    data = json.dumps(context, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")

@auth_token(allow_anonymous=True)
@ratelimit(group='rest', key='user_or_ip', rate=minute_rate)
@ratelimit(group='rest', key='user_or_ip', rate=hour_rate)
@ratelimit_warning
def user_job_download(request, aid, format, **kwargs):
    """
    Download the results of a completed job.
    """
    user = request.user
    args = []
    analysis = Analysis.fetch_by_aid_or_token(aid)

    if not analysis:
        return HttpResponse(status = 403)
    
    if not analysis.is_owner_or_anonymous(user.id):
        return HttpResponse(status=401)

    if not analysis.is_complete:
        return HttpResponse(status=204)

    format = format.lower()
    if format not in formatter.downloadformats:
        return HttpResponse(status=400)

    if format == 'genbank':
        islandset = GenomicIsland.objects.filter(aid_id=analysis.aid).order_by('start').all()
    else:
        islandset = GenomicIsland.island_gene_set(analysis.aid)

    args.append(islandset)
    p = None
    if format == 'genbank' or format == 'fasta':
        try:
            p = fetcher.GenbankParser(analysis.aid)
        except ValueError as e:
            response = HttpResponseServerError(reason='Unable to parse Genbank')
            response.content = e.message
            return response

    args.append(p)

    args.append(['integrated'] + formatter.allowedmethods)
    filename = analysis.generate_filename + '.' + formatter.downloadextensions[format]
    args.append(filename)
    
    response = formatter.downloadformats[format](*args)
    
    return response

@auth_token(allow_anonymous=True)
@ratelimit(group='rest', key='user_or_ip', rate=minute_rate)
@ratelimit(group='rest', key='user_or_ip', rate=hour_rate)
@ratelimit_warning
def ref_genomes(request, **kwargs):
    """
    Fetch a list of the available reference genomes for Islandpick jobs.
    """

    genomes = list(NameCache.objects.filter(isvalid=1).annotate(ref_accnum=F('cid')).values('ref_accnum', 'name').all())

    data = json.dumps(genomes, indent=4, sort_keys=False)

    return HttpResponse(data, content_type="application/json")

@csrf_exempt
@auth_token(allow_anonymous=True)
@ratelimit(group='rest_submit', key='user_or_ip', rate=submission_minute_rate)
@ratelimit(group='rest_submit', key='user_or_ip', rate=submission_hour_rate)
@ratelimit(group='rest_submit', key='user_or_ip', rate=submission_day_rate)
@ratelimit_warning
def user_job_submit(request, **kwargs):
    """
    Upload a genome as a new job.
    """
    user = request.user

    if request.method != 'POST':
        return HttpResponse(status=403)

    return _uploadcustomajax(request)#, userid=user.id)
