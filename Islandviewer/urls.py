from django.conf.urls import include, url
import settings.env

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

if settings.env.DEV_ENV:
    urlpatterns = [
        url(r'^islandviewer/', include('webui.urls')),
        url(r'', include('iv_social.urls', namespace='iv_social')),
        url(r'', include('social_django.urls', namespace='social')),
      
    # Examples:
    # url(r'^$', 'Islandviewer.views.home', name='home'),
    # url(r'^Islandviewer/', include('Islandviewer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    ]
else:
    urlpatterns = [
        url(r'^', include('webui.urls')),
        url(r'', include('iv_social.urls', namespace='iv_social')),
        url(r'', include('social_django.urls', namespace='social')),
    ]
    
