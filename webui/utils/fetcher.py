from django.conf import settings
from webui.models import Analysis, GenomicIsland, GC, CustomGenome, IslandGenes, UploadGenome, Virulence, Genes, Replicon, Genomeproject, STATUS, STATUS_CHOICES

from .formatter import formatResults

def fetchgenes(aid, methods, format):

    params = [aid]
    genes = Genes.objects.raw("SELECT GenomicIsland.*, Genes.* FROM Genes, IslandGenes, GenomicIsland WHERE GenomicIsland.aid_id = %s AND GenomicIsland.gi = IslandGenes.gi AND Genes.id = IslandGenes.gene_id ORDER BY GenomicIsland.prediction_method, Genes.start", params)
    
    resultstr = formatResults(genes, format, methods)
    
    return resultstr

def fetchGenbankFile(accession):
    genomeproject = Genomeproject.objects.using("microbedb").raw("SELECT genomeproject.gpv_directory FROM genomeproject, replicon WHERE genomeproject.	gpv_id = replicon.gpv_id AND replicon.rep_accum = %s",[accession])
    fileDirectory = genomeproject[0].gpv_directory
    file = open(fileDirectory,'r')
    return file


