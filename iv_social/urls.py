from django.conf.urls import url

from . import views

urlpatterns = [
#    url(r'^$', views.index, name='index'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^user/jobs/$', views.user_jobs, name='user_jobs'),
    url(r'^user/jobs/json/$', views.user_jobs_json, name='user_jobs_json'),
    url(r'^user/token/$', views.user_token, name='user_rest_token'),
    url(r'^user/token/reset/$', views.user_reset_token, name='user_rest_token_reset'),
]
