from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.conf import settings
from datetime import datetime
import pytz
import json
import uuid
from models import UserToken, PICKER_DEFAULTS

def auth_token(function=None):
    def decorator(view_func):
        def decorated(request, *args, **kwargs):

            if 'iv_social' in settings.INSTALLED_APPS:
                try:
                    token = request.META['HTTP_X_AUTHTOKEN']

                    uuid.UUID(token)
                    usertoken = UserToken.objects.get(token=token)

                    if usertoken.expires < datetime.now(pytz.utc):
                        return HttpResponse(status=401)                    

                except Exception as e:
                    if settings.DEBUG:
                        print str(e)
                    return HttpResponse(status=401)

                # Set the authenticated user for the request
                request.user = usertoken.user

            response = view_func(request, *args, **kwargs)

            return response

        decorated.__name__ = view_func.__name__
        decorated.__dict__ = view_func.__dict__
        decorated.__doc__ = view_func.__doc__

        return decorated

    if function is None:
        return decorator
    else:
        return decorator(function)

def ratelimit_warning(function=None):
    def decorator(view_func):
        def decorated(request, *args, **kwargs):

            if getattr(request, 'limited', False):
                context = {'status': 429, 'error': 'Your request has been rate limited, please wait and try again later'}

                data = json.dumps(context, indent=4, sort_keys=False)

                return HttpResponse(data, content_type="application/json", status=429)

            response = view_func(request, *args, **kwargs)

            return response

        decorated.__name__ = view_func.__name__
        decorated.__dict__ = view_func.__dict__
        decorated.__doc__ = view_func.__doc__

        return decorated

    if function is None:
        return decorator
    else:
        return decorator(function)

def parameter_parser(function=None, allow_methods=('GET', 'POST')):
    
    def decorator(view_func):
        def decorated(request, *args, **kwargs):
            
            if request.method == 'POST' and request.method in allow_methods:
                json_data = json.loads(request.body)
                kwargs.update(json_data)
            elif request.method == 'GET' and request.method in allow_methods:
                pass
            else:
                return HttpResponse(status=403)

            get_params = request.GET.dict()
            kwargs.update(get_params)
                            
            response = view_func(request, *args, **kwargs)
            
            if isinstance(response, (HttpResponse, HttpResponseRedirect, StreamingHttpResponse)):
                return response   
            
        decorated.__name__ = view_func.__name__
        decorated.__dict__ = view_func.__dict__
        decorated.__doc__ = view_func.__doc__

        return decorated
        
    if function is None:
        return decorator
    else:
        return decorator(function)
    
def scrub_picker(function=None, remove_keys=None):
    """
    Decorator to scrub the results of the islandpick picker before they go back
    to the user, there's some internal things they don't need to see.
    """
    def decorator(view_func):
        def decorated(request, *args, **kwargs):
                            
            response = view_func(request, *args, **kwargs)
            
            if isinstance(response, (HttpResponse, HttpResponseRedirect, StreamingHttpResponse)):
                return response
            
            '''
            Now go through the response object and clean the results before we send
            them back to the user, things the user should never see
            '''
            if 'parameters' in response:
                for p in ['workdir', 'microbedb_ver']:
                    response['parameters'].pop(p, None)

                response['parameters']['min_gi_size'] = response['parameters'].pop('MIN_GI_SIZE', PICKER_DEFAULTS['min_gi_size'])
                for p in PICKER_DEFAULTS:
                    if p not in response['parameters']:
                        response['parameters'][p] = PICKER_DEFAULTS[p]

            for p in remove_keys or []:
                response.pop(p, None)

            data = json.dumps(response, indent=4, sort_keys=False)

            return HttpResponse(data, content_type="application/json")

        decorated.__name__ = view_func.__name__
        decorated.__dict__ = view_func.__dict__
        decorated.__doc__ = view_func.__doc__

        return decorated
        
    if function is None:
        return decorator
    else:
        return decorator(function)
