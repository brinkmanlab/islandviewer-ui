from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='index'),
    url(r'^rest/jobs/$', views.user_jobs, name='user_jobs'),
    url(r'^rest/job/(?P<aid>\d+)/$', views.user_job, name='user_job'),
    url(r'^rest/job/(?P<aid>\d+)/islandpick/$', views.user_job_islandpick, name='user_job_islandpick'),
    url(r'^rest/job/(?P<aid>\d+)/islandpick/picker/$', views.user_job_picker, name='user_job_picker'),
    url(r'^rest/job/(?P<aid>\d+)/islandpick/rerun/$', views.user_job_islandpick_rerun, name='user_job_islandpick_rerun'),
    url(r'^rest/job/(?P<aid>\d+)/download/(?P<format>\w+)/$', views.user_job_download, name='user_job_download'),
    url(r'^rest/job/submit/$', views.user_job_submit, name='user_job_submit'),
    url(r'^rest/genomes/$', views.ref_genomes, name='ref_genomes'),
]
