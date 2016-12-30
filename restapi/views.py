from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.db.models import F

import json
from ratelimit.decorators import ratelimit

from webui.models import Analysis, CustomGenome, GenomicIsland, NameCache, Notification, STATUS_CHOICES, GI_MODULES
from webui.views import _uploadcustomajax
from webui.decorators import auth_token, ratelimit_warning
from webui.utils import formatter
from giparser import fetcher

@auth_token
@ratelimit(group='rest', key='user', rate='10/m')
@ratelimit(group='rest', key='user', rate='120/h')
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

        analysis_set.append({'aid': a.aid,
                             'results': request.build_absolute_uri( reverse('results', kwargs={'aid': a.aid}) ) + ("?token={}".format(a.token) if a.token else ''),

                            'genome_name': genome.name,
                            'status': CHOICES[a.status],
                            })

    data = json.dumps(analysis_set, indent=4, sort_keys=False)

    return HttpResponse(data, content_type="application/json")

@auth_token
@ratelimit(group='rest', key='user', rate='10/m')
@ratelimit(group='rest', key='user', rate='120/h')
@ratelimit_warning
def user_job(request, aid, **kwargs):
    user = request.user
    analysis = Analysis.objects.select_related().get(pk=aid)
    CHOICES = dict(STATUS_CHOICES)
    context = {}

    if not analysis.is_owner(user.id):
        return HttpResponse(status=401)
    
    context['aid'] = analysis.aid
    context['status'] = CHOICES[analysis.status]
    context['results'] = request.build_absolute_uri( reverse('results', kwargs={'aid': analysis.aid}) ) + ("?token={}".format(analysis.token) if analysis.token else '')

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

@auth_token
@ratelimit(group='rest', key='user', rate='10/m')
@ratelimit(group='rest', key='user', rate='120/h')
@ratelimit_warning
def user_job_download(request, aid, format, **kwargs):
    user = request.user
    args = []
    analysis = Analysis.objects.select_related().get(pk=aid)
    
    if not analysis.is_owner(user.id):
        return HttpResponse(status=401)

    if not analysis.is_complete:
        return HttpResponse(status=204)

    format = format.lower()
    if format not in formatter.downloadformats:
        return HttpResponse(status=400)

    if format == 'genbank':
        islandset = GenomicIsland.objects.filter(aid_id=aid).order_by('start').all()
    else:
        islandset = GenomicIsland.island_gene_set(aid)

    args.append(islandset)
    if format == 'genbank' or format == 'fasta':
        p = fetcher.GenbankParser(aid)
        args.append(p)

    args.append(['integrated'] + formatter.allowedmethods)
    filename = analysis.generate_filename + '.' + formatter.downloadextensions[format]
    args.append(filename)
    
    response = formatter.downloadformats[format](*args)
    
    return response

@auth_token
@ratelimit(group='rest', key='user', rate='10/m')
@ratelimit(group='rest', key='user', rate='120/h')
@ratelimit_warning
def ref_genomes(request, **kwargs):

    genomes = list(NameCache.objects.filter(isvalid=1).annotate(ref_accnum=F('cid')).values('ref_accnum', 'name').all())

    data = json.dumps(genomes, indent=4, sort_keys=False)

    return HttpResponse(data, content_type="application/json")

@csrf_exempt
@auth_token
@ratelimit(group='rest_submit', key='user', rate='10/h')
@ratelimit(group='rest_submit', key='user', rate='50/d')
@ratelimit_warning
def user_job_submit(request, **kwargs):
    user = request.user
    
    if request.method != 'POST':
        return HttpResponse(status=403)

    # If we were rate limited, return a watning to the user
    if getattr(request, 'limited', False):
        return ratelimit_warning(request)

    return _uploadcustomajax(request, userid=user.id)
