from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout, login

import json

from webui.models import Analysis, CustomGenome, UserToken, STATUS_CHOICES
from usermanager.token import generate_token, reset_token

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return HttpResponseRedirect(reverse('browse'))

@login_required
def user_jobs(request):
    """
    Show a registered user their jobs
    """
    return render(request, 'userjobs.html')

@login_required
def user_jobs_json(request):
    context = {}

    context['sEcho'] = 1
    if(request.GET.get('sEcho')):
        sEcho = request.GET.get('sEcho')
        if not sEcho.isdigit():
            return HttpResponse(status=400)

 #       print "Setting secho to: " + sEcho
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

    user_id = request.user.id
    analysis = Analysis.objects.filter(owner_id=user_id).order_by('-aid').all()

    context['iTotalRecords'] = len(analysis)
    context['iTotalDisplayRecords'] = len(analysis)
        
    analysis_set = []
    for a in analysis[startAt:endAt]:
        """A big assumption! That it's a custom genome.
           Fetching genome names (done multiple places) should be
           abstracted out at some point."""
        genome = CustomGenome.objects.get(pk=a.ext_id)

        analysis_set.append({'aid': a.aid,
                            'genome_name': genome.name,
                            'status': STATUS_CHOICES[a.status][1],
                            'token': a.token})

    context['aaData'] = analysis_set

    data = json.dumps(context, indent=4, sort_keys=False)
#    data = serializers.serialize('json', context)

    return HttpResponse(data, content_type="application/json")

@login_required
def user_token(request):
    context = {}

    user = request.user
    user_token, create = UserToken.objects.get_or_create(user=user)

    if create:
        user_token = generate_token(user, user_token)
        
    context['token'] = user_token.token
    context['tokenexpiry'] = user_token.expires.strftime('%Y-%m-%d %H:%M')

    return render(request, 'usertoken.html', context)

@login_required
def user_reset_token(request):

    user = request.user
    user_token = UserToken.objects.get(user=user)
    
    user_token = reset_token(user_token)
    
    data = json.dumps({'token': str(user_token.token), 'expiry': user_token.expires.strftime('%Y-%m-%d %H:%M')}, indent=4, sort_keys=False)
    
    return HttpResponse(data, content_type="application/json")    
