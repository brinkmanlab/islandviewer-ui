from django.conf import settings
from webui.models import Analysis, GenomicIsland, GC, CustomGenome, IslandGenes, UploadGenome, Virulence, Genes, Replicon, Genomeproject, STATUS, STATUS_CHOICES
from .formatter import formatResults

def fetchgenes(aid, methods, format):

    params = [aid]
    genes = Genes.objects.raw("SELECT GenomicIsland.*, Genes.* FROM Genes, IslandGenes, GenomicIsland WHERE GenomicIsland.aid_id = %s AND GenomicIsland.gi = IslandGenes.gi AND Genes.id = IslandGenes.gene_id ORDER BY GenomicIsland.prediction_method, Genes.start", params)
    
    resultstr = formatResults(genes, format, methods)
    
    return resultstr

def fetchGenbankFile(accession):
    replicon = Replicon.objects.using('microbedb').filter(rep_accnum__exact=accession)[0]
    key = replicon.gpv_id
    project = Genomeproject.objects.usig('microbedb').filter(gpv_id__exact=key).order_by('release_date')
    print project[0].gpv_directory

