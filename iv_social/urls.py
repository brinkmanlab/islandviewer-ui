from django.urls import re_path

from . import views
app_name = 'iv_social'
urlpatterns = [
#    re_path(r'^$', views.index, name='index'),
    re_path(r'^logout/$', views.logout, name='logout'),
    re_path(r'^user/jobs/$', views.user_jobs, name='user_jobs'),
    re_path(r'^user/jobs/json/$', views.user_jobs_json, name='user_jobs_json'),
    re_path(r'^user/token/$', views.user_token, name='user_rest_token'),
    re_path(r'^user/token/reset/$', views.user_reset_token, name='user_rest_token_reset'),
]
