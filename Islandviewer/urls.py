from django.urls import include, re_path
from .settings import env

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

if env.DEV_ENV:
    urlpatterns = [
        re_path(r'^islandviewer/', include('webui.urls')),
        re_path(r'^islandviewer/', include('iv_social.urls', namespace='iv_social')),
        re_path(r'^islandviewer/', include('social_django.urls', namespace='social')),
        re_path(r'^islandviewer/', include('restapi.urls', namespace='restapi')),

    # Examples:
    # re_path(r'^$', 'Islandviewer.views.home', name='home'),
    # re_path(r'^Islandviewer/', include('Islandviewer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # re_path(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # re_path(r'^admin/', include(admin.site.urls)),
    ]
else:
    urlpatterns = [
        re_path(r'^', include('webui.urls')),
        re_path(r'', include('iv_social.urls', namespace='iv_social')),
        re_path(r'', include('social_django.urls', namespace='social')),
        re_path(r'', include('restapi.urls', namespace='restapi')),
    ]
    
