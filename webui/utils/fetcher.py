from django.conf import settings
from webui.models import Analysis, GenomicIsland, GC, CustomGenome, IslandGenes, UploadGenome, Virulence, Genes, Replicon, Genomeproject, STATUS, STATUS_CHOICES
from django.db import connections
from .formatter import formatResults

def fetchgenes(aid, methods, format):

    params = [aid]
    genes = Genes.objects.raw("SELECT GenomicIsland.*, Genes.* FROM Genes, IslandGenes, GenomicIsland WHERE GenomicIsland.aid_id = %s AND GenomicIsland.gi = IslandGenes.gi AND Genes.id = IslandGenes.gene_id ORDER BY GenomicIsland.prediction_method, Genes.start", params)
    
    resultstr = formatResults(genes, format, methods)
    
    return resultstr

def fetchGenbankFile(accession):
    cursor = connections['microbedb'].cursor()
    sql = "SELECT genomeproject.gpv_directory FROM genomeproject, replicon WHERE genomeproject.	gpv_id = replicon.gpv_id AND replicon.rep_accnum = \""+accession+"\";"

    print sql
    cursor.execute(sql)

    row = cursor.fetchone()
    print row


