from django.conf import settings

def auth_enabled(request):
    """
    Context processor, if the iv_social app is active,
    place a variable in the context saying so.
    """
    if 'iv_social' in settings.INSTALLED_APPS:
        return {'iv_social': True}

    return {}
