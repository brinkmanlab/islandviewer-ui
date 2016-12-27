from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
import pytz
import json
import uuid
from models import UserToken

def auth_token(function=None):
    def decorator(view_func):
        def decorated(request, *args, **kwargs):

            try:
                token = request.META['HTTP_X_AUTHTOKEN']

                uuid.UUID(token)
                usertoken = UserToken.objects.get(token=token)

                if usertoken.expires < datetime.now(pytz.utc):
                    return HttpResponse(status=403)                    

                # Do rate limit check here


            except Exception as e:
                if settings.DEBUG:
                    print str(e)
                return HttpResponse(status=403)

            # Set the authenticated user for the request
            request.user = usertoken.user

            response = view_func(request, *args, usertoken=usertoken, **kwargs)

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
                context = {'status': 500, 'error': 'Your request has been rate limited, please wait and try again later'}

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
