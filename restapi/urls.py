from django.urls import re_path

from . import views
app_name = 'iv_social'
urlpatterns = [
#    re_path(r'^$', views.index, name='index'),
    re_path(r'^rest/jobs/$', views.user_jobs, name='user_jobs'),
    re_path(r'^rest/job/(?P<aid>\w+)/$', views.user_job, name='user_job'),
    re_path(r'^rest/job/(?P<aid>\w+)/islandpick/$', views.user_job_islandpick, name='user_job_islandpick'),
    re_path(r'^rest/job/(?P<aid>\w+)/islandpick/picker/$', views.user_job_picker, name='user_job_picker'),
    re_path(r'^rest/job/(?P<aid>\w+)/islandpick/rerun/$', views.user_job_islandpick_rerun, name='user_job_islandpick_rerun'),
    re_path(r'^rest/job/(?P<aid>\w+)/download/(?P<format>\w+)/$', views.user_job_download, name='user_job_download'),
    re_path(r'^rest/submit/$', views.user_job_submit, name='user_job_submit'),
    re_path(r'^rest/genomes/$', views.ref_genomes, name='ref_genomes'),
]
