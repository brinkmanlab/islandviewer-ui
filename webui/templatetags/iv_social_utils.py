from django import template

register = template.Library()

@register.simple_tag
def social_menu():
    """
    A dummy template tag that is used if the iv_social
    module isn't loaded. This is why webui must be loaded
    first in the apps, then iv_social, so iv_social
    template tags take precedence.
    """
    
    return ''
