from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import pprint
#from Bio.Phylo.TreeConstruction import _DistanceMatrix, DistanceTreeConstructor
from Bio import Phylo
import StringIO
import json, os

STATUS = {'PENDING':1,'RUNNING':2,'ERROR':3,'COMPLETE':4}
STATUS_CHOICES = [
    (STATUS['PENDING'], 'Pending'),
    (STATUS['RUNNING'], 'Running'),
    (STATUS['ERROR'], 'Error'),
    (STATUS['COMPLETE'], 'Complete'),
]

VIRULENCE_FACTORS = {
    'VFDB': 'Virulence factors',
    'ARDB': 'Resistance genes',
    'PAG': 'Pathogen-associated genes'
}

VIRULENCE_FACTOR_CATEGORIES = {
    'VFDB': 'VFDB',
    'Victors': 'VFDB',
    'PATRIC_VF': 'VFDB',
    'ARDB': 'ARDB',
    'CARD': 'ARDB',
    'BLAST': 'BLAST',
    'RGI': 'RGI',
    'PAG': 'PAG' 
}

MODULES = ['Prepare', 'Distance', 'Sigi', 'Dimob', 'Islandpick', 'Virulence', 'Summary']
GI_MODULES = ['Sigi', 'Dimob', 'Islandpick']

PICKER_DEFAULTS = {
    'min_gi_size': 4000,
    'min_cutoff': 0.00,
    'max_cutoff': 0.215,
}

class CustomGenome(models.Model):
    cid = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    owner_id = models.IntegerField(default=0)
    cds_num = models.IntegerField(default=0)
    rep_size = models.IntegerField(default=0)
    filename = models.CharField(max_length=100, blank=True, null=True)
    formats = models.CharField(max_length=50)
    contigs = models.IntegerField(default=1)
    genome_status = models.IntegerField()
    submit_date = models.DateTimeField('date submitted', auto_now_add=True)

    @property
    def isvalid(self):
        return self.genome_status == 6

    @property
    def is_system_owned(self):
        return False

    def is_owner(self, uid):
        return uid == self.owner_id

    class Meta:
        db_table = "CustomGenome"

class NameCache(models.Model):
    cid = models.CharField(max_length=24, unique=True)
    name = models.CharField(max_length=100)
    cds_num = models.IntegerField(default=0)
    rep_size = models.IntegerField(default=0)
    isvalid = models.IntegerField(default=1)

    '''
    Make a NameCache item look like a CustomGenome so they can more easily
    be used interchangably to clean the code up.
    '''
        
    @property
    def replicon(self):
        if not hasattr(self, '_rep'):
            self._rep = Replicon.by_accnum(self.cid)
            
        return self._rep
    
    @property
    def owner_id(self):
        return 0

    def is_owner(self, uid):
        return False

    @property
    def is_system_owned(self):
        return True
    
    @property
    def filename(self):
        rep = self.replicon
        if rep:
            return rep.base_path

    @property
    def formats(self):
        rep = self.replicon
        if rep:
            return rep.file_types

    @property
    def contigs(self):
        return 1

    @property
    def genome_status(self):
        return 6

    class Meta:
        db_table = "NameCache"

class Analysis(models.Model):
    CUSTOM = 1
    MICROBEDB = 2
    ATYPE_CHOICES = (
        (CUSTOM, 'Custom'),
        (MICROBEDB, 'MicrobeDB'),
    )
    aid = models.AutoField(primary_key=True)
    atype = models.IntegerField(choices=ATYPE_CHOICES,
                                default=CUSTOM)
    ext_id = models.CharField(max_length=24)
    owner_id = models.IntegerField(default=0)
    token = models.CharField(max_length=22, null=True, blank=True)
    default_analysis = models.BooleanField(default=True)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS['PENDING'])
    workdir = models.CharField(max_length=100)
    microbedb_ver = models.IntegerField(default=0)
    start_date = models.DateTimeField('date started', null=True)
    complete_date = models.DateTimeField('date completed', null=True)

    @classmethod
    def fetch_by_aid_or_token(cls, id):

        try:
            int(id)
            analysis = cls.objects.get(pk=id)
            return analysis
        except Analysis.DoesNotExist:
            '''
            If we get a DoesNotExist exception, it was obviously an aid but we couldn't find it,
            anything else fall through and try to look up as a token
            '''
            return None
        except Exception as e:
            if settings.DEBUG:
                print e
            pass
        
        try:
            analysis = cls.objects.get(token=id)
            return analysis
        except Analysis.DoesNotExist:
            '''
            If we get a DoesNotExist exception, it was obviously an aid but we couldn't find it,
            anything else fall through and try to look up as a token
            '''
            pass
        except Exception as e:
            '''
            If we get some other exception here, something really bad has gone wrong,
            let's try to log something if we're debugging
            '''
            if settings.DEBUG:
                print e
            pass

        return None

    @property
    def is_complete(self):
        return self.status == STATUS['COMPLETE']
    
    @property
    def is_precomputed(self):
        return self.atype == Analysis.MICROBEDB
    
    @property
    def is_custom(self):
        return self.atype == Analysis.CUSTOM
    
    @property
    def is_system_owned(self):
        return self.owner_id == 0

    def valid_token(self, token):
        if self.token and not self.is_system_owned:
            return token == self.token
        
        return True

    @property
    def generate_filename(self):
        if self.is_precomputed:
            return self.ext_id
        elif self.is_custom:
            return ''.join(e for e in self.genome.name if e.isalnum())

    def is_owner(self, uid, precomputed_ok=True):
        """
        Check if the given user id owns the analysis,
        optional parameter which by default allows analysis owned
        by the system user (pre-computed) to be disallowed.
        """
        if self.owner_id == 0 and precomputed_ok:
            return True
        elif self.owner_id == uid:
            return True
        
        return False

    @property
    def genome(self):
        if not hasattr(self, '_genome'):
            if self.atype == Analysis.CUSTOM:
                self._genome = CustomGenome.objects.get(pk=self.ext_id)
            elif self.atype == Analysis.MICROBEDB:
                self._genome = NameCache.objects.get(cid=self.ext_id)
                
        return self._genome

    # Specialty function to find an analysis with the same 
    # Islandpick settings (comparison genomes, min_gi_size)
    
    @classmethod
    def find_islandpick(cls, ext_id, genomes, min_gi_size):
    
        min_gi_size = int(min_gi_size)
        if settings.DEBUG:
            print "Testing for existing islandpick using, ext_id {}, using: ".format(ext_id)
            print "Looking for min_gi_size: {} and genomes {}".format(min_gi_size, genomes)
            
        analysis = Analysis.objects.filter(ext_id = ext_id)
        
        for a in analysis:
            a_parameters_json = None
            for task in a.tasks.all():
                if task.prediction_method == 'Islandpick':
                    a_parameters_json = task.parameters
                    break
            
            # We found an Islandpick in that analysis
            if a_parameters_json:
                if settings.DEBUG:
                    print "Checking Islandpick in analysis {}".format(a.aid)
                a_parameters = json.loads(a_parameters_json)
                
                if settings.DEBUG:
                    print "Found parameters:"
                    pprint.pprint(a_parameters)
                
                # First check we have the right fields...
                if 'comparison_genomes' not in a_parameters or 'MIN_GI_SIZE' not in a_parameters:
                    if settings.DEBUG:
                        print "Either comparison_genomes or min_gi_size aren't in the db for analysis {}, skipping".format(a.aid)
                    continue

                # Next check the comparison genomes
                if sorted(a_parameters['comparison_genomes'].split(' ')) != sorted(genomes):
                    if settings.DEBUG:
                        print "comparison_genomes for analysis {} don't match, skipping".format(a.aid)
                    continue
                
                # Finally, does the min_gi_size match?
                if int(a_parameters['MIN_GI_SIZE']) != min_gi_size:
                    if settings.DEBUG:
                        print "min_gi_size for analysis {} doesn't match, skipping".format(a.aid)
                    continue
                
                # We made it this far, we must have a match, return this aid
                return (a.aid, a.token)
            
        # We exited the loop without returning, we must not have
        # a match, return None
        return None 

    def find_reference_genome(self):
        
        a_parameters_json = None
        for task in self.tasks.all():
            if task.prediction_method == 'Prepare':
                a_parameters_json = task.parameters
                break
            
        # We found a Prepare task, let's see if it has a ref_accnum
        if a_parameters_json:
            a_parameters = json.loads(a_parameters_json)
            
            if settings.DEBUG:
                print "Found parameters:"
                pprint.pprint(a_parameters)
            
            if 'ref_accnum' in a_parameters:
                return a_parameters['ref_accnum']
            
        return None
    
    @classmethod
    def lookup_genome(cls, accnum):
        
        try:
            float(accnum)
        except ValueError:
            # It's not a custom genome...
            genome = NameCache.objects.get(cid=accnum)
            return genome
        
        # It's a custom genome
        genome = CustomGenome.objects.get(cid=accnum)
        return genome

    @classmethod
    def last_modified(cls, request, aid):
        
        return Analysis.objects.get(aid=aid).complete_date

    class Meta:
        db_table = "Analysis"
#        permissions = (
#            ("view_analysis", "Can see all analysis"),
#            ("upgrade_users", "Can see and upgrade users"),
#        )

class GIAnalysisTask(models.Model):
    taskid = models.AutoField(primary_key=True)
    aid = models.ForeignKey(Analysis, related_name='tasks')
    prediction_method = models.CharField(max_length=15)
    status = models.IntegerField(choices=STATUS_CHOICES,
                                 default=STATUS['PENDING'])
    parameters = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField('date started', null=True)
    complete_date = models.DateTimeField('date completed', null=True)

    @classmethod
    def fetch_parameters(cls, aid, method):
            
        try:
            if settings.DEBUG:
                print "Checking method {} in analysis {}".format(method,aid)

            task = GIAnalysisTask.objects.filter(aid=aid, prediction_method=method)
            a_parameters_json = task.parameters
            
            a_parameters = json.loads(a_parameters_json)

            if settings.DEBUG:
                print "Found parameters:"
                pprint.pprint(a_parameters)

        except Exception as e:
            if settings.DEBUG:
                print e
                
            raise e
        
        return a_parameters
        
    class Meta:
        db_table = "GIAnalysisTask"

class GenomicIsland(models.Model):
    gi = models.AutoField(primary_key=True)
    aid = models.ForeignKey(Analysis)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    prediction_method = models.CharField(max_length=15, db_index=True)
    details = models.CharField(max_length=20, blank=True, null=True)

    @classmethod
    def island_gene_set(cls, aid):
        params = [aid] 

        islandset = Genes.objects.raw("SELECT G.id, GI.gi AS gi, GI.start AS island_start, GI.end AS island_end, GI.prediction_method, G.ext_id, G.start AS gene_start, G.end AS gene_end, G.strand, G.name, G.gene, G.product, G.locus, GROUP_CONCAT( DISTINCT V.source ) AS virulence FROM Genes AS G JOIN IslandGenes AS IG ON G.id = IG.gene_id JOIN GenomicIsland AS GI ON GI.gi = IG.gi LEFT JOIN virulence_mapped AS V ON G.name = V.protein_accnum WHERE GI.aid_id = %s GROUP BY IG.id ORDER BY GI.start, GI.prediction_method", params)

        return islandset

    @classmethod
    def sqltodict(cls, query,param):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute(query,param)
        fieldnames = [name[0] for name in cursor.description]
        result = []
        for row in cursor.fetchall():
            rowset = []
            for field in zip(fieldnames, row):
                rowset.append(field)
            result.append(dict(rowset))
        return result

    class Meta:
        db_table = "GenomicIsland"
        index_together = ['aid', 'prediction_method']

class GC(models.Model):
    ext_id = models.CharField(primary_key=True,max_length=24)
    min = models.FloatField()
    max = models.FloatField()
    mean = models.FloatField()
    gc = models.TextField()
    
    class Meta:
        db_table = "GC"

class Genes(models.Model):
    ext_id = models.CharField(max_length=24)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    strand = models.IntegerField()
    name = models.CharField(max_length=18, blank=True, null=True)
    gene = models.CharField(max_length=10, blank=True, null=True)
    product = models.CharField(max_length=100, blank=True, null=True)
    locus = models.CharField(max_length=20, blank=True, null=True)
    
    class Meta:
        db_table = "Genes"
        # dup_catcher index
        unique_together = ('ext_id', 'start', 'end')

class IslandGenes(models.Model):
    gi = models.IntegerField(db_index=True)
    gene = models.ForeignKey(Genes, db_index=True)
    
    class Meta:
        db_table = "IslandGenes"

class Distance(models.Model):
    rep_accnum1 = models.CharField(max_length=24)
    rep_accnum2 = models.CharField(max_length=24)
    distance = models.FloatField()

    @classmethod
    def find_genomes(cls, accnum, *args, **kwargs):
        #pprint.pprint(kwargs)
        
        if 'min_cutoff' in kwargs:
            min_cutoff = kwargs['min_cutoff']
        else:
            min_cutoff = PICKER_DEFAULTS['min_cutoff']

        if 'max_cutoff' in kwargs:
            max_cutoff = kwargs['max_cutoff']
        else:
            max_cutoff = PICKER_DEFAULTS['max_cutoff']

        params = [accnum, accnum, min_cutoff, max_cutoff]
        sql = "SELECT id, rep_accnum1, rep_accnum2, distance from Distance WHERE (rep_accnum1 = %s or rep_accnum2 = %s) AND "
        sql_dist = "(distance >= %s AND distance <= %s)"

        if 'extra_genomes' in kwargs:
            rep_list = ','.join("'" + rep + "'" for rep in kwargs['extra_genomes'])
            sql += "(" + sql_dist + " OR (rep_accnum1 IN ({}) OR rep_accnum2 IN ({})))".format(rep_list, rep_list)
        else:
            sql += sql_dist
        
        #sql += ' ORDER BY distance'
        
        dists = Distance.objects.raw(sql, params)
        #dists = Distance.objects.filter(models.Q(rep_accnum1=accnum) | models.Q(rep_accnum2=accnum), distance__gte=min_cutoff, distance__lte=max_cutoff).order_by('distance')
        
        genomes = [(g.rep_accnum1, g.distance) if g.rep_accnum1 != accnum else (g.rep_accnum2, g.distance) for g in dists]

        return genomes
    
    @classmethod
    def distance_matrix(cls, cluster_list):
        print cluster_list
        dists = Distance.objects.filter(rep_accnum1__in=cluster_list, rep_accnum2__in=cluster_list)
        
        distance_pairs = {g.rep_accnum1 + '_' + g.rep_accnum2: g.distance for g in dists.all()}
    
        matrix = []
        for i in range(0,len(cluster_list)):
            matrix_iteration = []
            for j in range(0,i+1):
                if i == j:
                    matrix_iteration.append(0)
                elif cluster_list[i] + '_' + cluster_list[j] in distance_pairs:
                    matrix_iteration.append(distance_pairs[cluster_list[i] + '_' + cluster_list[j]])
                elif cluster_list[j] + '_' + cluster_list[i] in distance_pairs:
                    matrix_iteration.append(distance_pairs[cluster_list[j] + '_' + cluster_list[i]])
                else:
                    raise("Error, can't find pair!")
            matrix.append(matrix_iteration)
            #print matrix_iteration

        cluster_list = [s.encode('ascii', 'ignore') for s in cluster_list]
        matrix_obj = _DistanceMatrix(names=cluster_list, matrix=matrix)
        constructor = DistanceTreeConstructor()
        tree = constructor.nj(matrix_obj)
        tree.ladderize()
        #Phylo.draw_ascii(tree)
        output = StringIO.StringIO()
        Phylo.write(tree, output, 'newick')
        tree_str = output.getvalue()
        #print tree_str
        
        return tree_str
    
    class Meta:
        db_table = "Distance"
        index_together = [
            ['rep_accnum1', 'rep_accnum2'],
            ['rep_accnum2', 'rep_accnum1'],
        ]

class UploadGenome(models.Model):
    id = models.AutoField(primary_key=True)
    filename = models.CharField(max_length=120, blank=True, null=True)
    ip_addr = models.GenericIPAddressField()
    genome_name = models.CharField(max_length=40, blank=True, null=True)
    email = models.EmailField()
    cid = models.IntegerField(default=0)
    date_uploaded = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "UploadGenome"

class Notification(models.Model):
    analysis = models.ForeignKey(Analysis, related_name='notifications')
    email = models.EmailField()
    status = models.IntegerField(default=0)
    
    class Meta:
        db_table = "Notification"
        unique_together = ('analysis', 'email')

class SiteStatus(models.Model):
    status = models.IntegerField(default=0, primary_key=True)
    message = models.CharField(max_length=500)
    class Meta:
        db_table = 'SiteStatus'
        
class Virulence(models.Model):
    protein_accnum = models.CharField(max_length=18,primary_key=True)
    external_id = models.CharField(max_length=18)
    source = models.IntegerField()
    type = models.IntegerField()
    flag = models.TextField(null=True, blank=True)
    pmid = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
#        managed = False
        db_table = 'virulence'

class VirulenceMapped(models.Model):
    gene_id = models.IntegerField(db_index=True)
    ext_id = models.CharField(max_length=24, null=True, blank=True)
    protein_accnum = models.CharField(max_length=18, null=True, blank=True, db_index=True)
    external_id = models.CharField(max_length=18, null=True, blank=True, db_index=True)
    source = models.IntegerField()
    type = models.IntegerField()
    flag = models.TextField(null=True, blank=True)
    pmid = models.CharField(max_length=50, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'virulence_mapped'
        unique_together = ('external_id', 'gene_id', 'ext_id')
        index_together = [
            ['ext_id', 'gene_id'],
        ]


class VirulenceCuratedReps(models.Model):
    rep_accnum = models.CharField(max_length=24, primary_key=True)

    class Meta:
        db_table = 'virulence_curated_reps'

class UserToken(models.Model):
    user = models.ForeignKey(User, unique=True)
    token = models.CharField(max_length=36)
    expires = models.DateTimeField(default=datetime.now()+timedelta(days=30), null=True)
    
    class Meta:
        db_table = 'UserToken'

'''
MicrobeDB models
'''

class Genomeproject(models.Model):
    gpv_id = models.IntegerField(primary_key=True, db_column='gpv_id')
    assembly_accession = models.CharField(max_length=20)
    asm_name = models.CharField(max_length=24)
    genome_name = models.TextField()
    version_id = models.ForeignKey('Version')
    bioproject = models.CharField(max_length=14)
    biosample = models.CharField(max_length=14)
    taxid = models.IntegerField(blank=True, null=True)
    species_taxid = models.IntegerField(blank=True, null=True)
    org_name = models.TextField(blank=True)
    infraspecific_name = models.CharField(max_length=24, null=True)
    submitter = models.TextField(blank=True)
    release_date = models.DateField(blank=True, null=True)
    gpv_directory = models.TextField(blank=True)
    filename = models.CharField(max_length=75)
    file_types = models.TextField(blank=True)
    prev_gpv = models.IntegerField(null=True)
    class Meta:
        managed = False
        db_table = 'genomeproject'

class Genomeproject_Checksum(models.Model):
    version_id = models.IntegerField(primary_key=True)
    filename = models.CharField(max_length=64)
    checksum = models.CharField(max_length=32)
    gpv_id = models.ForeignKey(Genomeproject, db_column='gpv_id')
    class Meta:
        managed = False
        db_table = 'genomeproject_checksum'
    
class Genomeproject_Meta(models.Model):
    gpv_id = models.OneToOneField(Genomeproject, db_column='gpv_id', on_delete=models.CASCADE, primary_key=True)
    gram_stain = models.CharField(max_length=7, blank=True, null=True)
    genome_gc = models.FloatField(blank=True, null=True)
    patho_status = models.CharField(max_length=11, blank=True, null=True)
    disease = models.TextField(blank=True, null=True)
    genome_size = models.FloatField(blank=True, null=True)
    pathogenic_in = models.TextField(blank=True, null=True)
    temp_range = models.CharField(max_length=17, blank=True, null=True)
    habitat = models.CharField(max_length=15, blank=True, null=True)
    shape = models.TextField(blank=True, null=True)
    arrangement = models.TextField(blank=True, null=True)
    endospore = models.CharField(max_length=7, blank=True, null=True)
    motility = models.CharField(max_length=7, blank=True, null=True)
    salinity = models.TextField(blank=True, null=True)
    oxygen_req = models.CharField(max_length=15, blank=True, null=True)
    chromosome_num = models.IntegerField(blank=True, null=True)
    plasmid_num = models.IntegerField(blank=True, null=True)
    contig_num = models.IntegerField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'genomeproject_meta'

class Replicon(models.Model):
    rpv_id = models.IntegerField(primary_key=True)
    gpv_id = models.ForeignKey('Genomeproject', related_name='replicons', db_column='gpv_id')
    version_id = models.IntegerField()
    rep_accnum = models.CharField(max_length=20, blank=True)
    rep_version = models.IntegerField()
    definition = models.TextField(blank=True)
    rep_type = models.CharField(max_length=10, blank=True)
    rep_ginum = models.TextField(blank=True)
    file_name = models.TextField(blank=True)
    file_types = models.TextField(blank=True)
    cds_num = models.IntegerField(blank=True, null=True)
    gene_num = models.IntegerField(blank=True, null=True)
    rep_size = models.IntegerField(blank=True, null=True)
    rna_num = models.IntegerField(blank=True, null=True)

    @property
    def base_path(self):
        return os.path.join(self.gpv_id.gpv_directory, self.file_name)

    @classmethod
    def by_accnum(cls, rep_accnum, rep_version=None):
        try:
            # If we haven't been given a version, see if we have one in the accession
            if not rep_version:
                split_accnum = rep_accnum.split('.')
                if len(split_accnum) == 2:
                    rep_accnum = split_accnum[0]
                    rep_version = split_accnum[1]

            lookup_param = {'rep_accnum': rep_accnum}
            if rep_version:
                lookup_param['rep_version'] = rep_version

            rep = cls.objects.using('microbedb').filter(**lookup_param).first()

            return rep
            
        except Exception as e:
            if settings.DEBUG:
                print str(e)
                
            return None

    class Meta:
        managed = False
        db_table = 'replicon'

class Taxonomy(models.Model):
    taxon_id = models.IntegerField(primary_key=True)
    superkingdom = models.TextField(blank=True, null=True)
    phylum = models.TextField(blank=True, null=True)
    tax_class = models.TextField(blank=True, null=True)
    order = models.TextField(blank=True, null=True)
    family = models.TextField(blank=True, null=True)
    genus = models.TextField(blank=True, null=True)
    species = models.TextField(blank=True, null=True)
    other = models.TextField(blank=True, null=True)
    synonyms = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'taxonomy'

class Version(models.Model):
    version_id = models.IntegerField(primary_key=True)
    dl_directory = models.TextField(blank=True)
    version_date = models.DateField()
    used_by = models.TextField(blank=True, null=True)
    is_current = models.IntegerField()
    class Meta:
        managed = False
        db_table = 'version'
