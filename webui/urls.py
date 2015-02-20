from django.conf.urls import patterns, url

from webui import views

urlpatterns = patterns('',
#    url(r'^$', views.index, name='index'),
    url(r'^$', views.showgenomes, name='browse'),
    url(r'^results/(?P<aid>\d+)/$', views.results, name='results'),
    url(r'^accession/(?P<accnum>\w+)/$', views.resultsbyrootaccnum, name='resultsbyrootaccnum'),
    url(r'^accession/(?P<accnum>\w+\.\d+)/$', views.resultsbyaccnum, name='resultsbyaccnum'),
    url(r'^islandpick/select/(?P<aid>\d+)/$', views.islandpick_select_genomes, name='islandpickselectgenomes'),
    url(r'^browse/$', views.showgenomes, name='browse'),
    url(r'^browse/json/$', views.showgenomesjson, name='browsejson'),
    url(r'^genomes/json/$', views.fetchgenomesjson, name='fetchgenomesjson'),
    url(r'^about/$', views.about, name='about'),
    url(r'^download/$', views.download, name='download'),
    url(r'^download/coordinates/$', views.downloadCoordinates, name='downloadcoordinates'),
    url(r'^download/annotations/$', views.downloadAnnotations, name='downloadannotations'),
    url(r'^download/sequences/$', views.downloadSequences, name='downloadsequences'),
    url(r'^resources/$', views.resources, name='resources'),
    url(r'^contactus/$', views.contactus, name='contactus'),
    url(r'^faq/$', views.faq, name='faq'),
    url(r'^islandpick/$', views.islandpick, name='islandpick'),
    url(r'acknowledgements', views.acknowledgements, name='acknowledgements'),
    url(r'^plot/(?P<aid>\d+)/$', views.circularplotjs, name='circularplotjs'),
    url(r'^json/gis/(?P<aid>\d+)/$', views.tablejson, name="tablejson"),
    url(r'^islands/$', views.fetchislands, name="fetchislands"),
    url(r'^islands/fasta/$', views.fetchislandsfasta, name="fetchislandsfasta"),
    url(r'^json/genes/(?P<gi_id>\d+)/$', views.genesjson, name="genesjson"),
    url(r'^json/genes/$', views.genesbybpjson, name="genesbybpjson"),
    url(r'^json/genes/search/(?P<ext_id>[\w\.]+)/$', views.search_genes, name="searchgenes"),
    url(r'^json/islandpick/(?P<aid>\d+)/$', views.islandpick_genomes, name="islandpick_genomes"),
    url(r'^notify/(?P<aid>\d+)/$', views.add_notify, name="add_notify"),
    url(r'^upload/$', views.uploadform, name="uploadform"),
    url(r'^ajax/upload/$', views.uploadcustomajax, name="uploadcustomajax"),
    url(r'^status/$', views.runstatus, name='runstatus'),
    url(r'^status/json/$', views.runstatusjson, name='runstatusjson'),
    url(r'^status/details/json/(?P<aid>\d+)/$', views.runstatusdetailsjson, name='runstatusdetailsjson'),
    url(r'^module/restart/(?P<aid>\d+)/$', views.restartmodule, name='restartmodule'),
    url(r'^module/logs/(?P<aid>\d+)/$', views.logsmodule, name='logsmodule'),
    url(r'^results/graph/(?P<aid>\d+)/$', views.graphanalysis, name='graphanalysis'),
    url(r'^results/graph/js/(?P<aid>\d+)/$', views.graphanalysisjs, name='graphanalysisjs'),
    url(r'^upload/(?P<upload_id>\d+)/$', views.uploadredirect, name='uploadredirect'),
)
