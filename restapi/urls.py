from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='index'),
    url(r'^rest/jobs/$', views.user_jobs, name='user_jobs'),
    url(r'^rest/job/(?P<aid>\d+)/$', views.user_job, name='user_job'),
    url(r'^rest/job/submit/$', views.user_job_submit, name='user_job_submit'),
    url(r'^rest/genomes/$', views.ref_genomes, name='ref_genomes'),
]
