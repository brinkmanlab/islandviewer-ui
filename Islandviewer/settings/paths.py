import os
import sys
import env

PROJECT_PATH  = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_PATH)
sys.path.insert(0, os.path.join(BASE_DIR, "lib"))

if env.PROD_ENV:
    CUSTOM_GENOMES = "/data/Modules/iv-backendV4/islandviewer/custom_genomes/"
    GENOME_UPLOAD_PATH = "/data/Modules/iv-backendV4/islandviewer/custom_genomes/tmp/"
    GENOME_SUBMISSION_SCRIPT = "/data/Modules/iv-backendV4/islandviewer/bin/submit_uploaded_genome.pl -c /data/Modules/iv-backendV4/islandviewer/etc/islandviewer.config -f {filename} -n \"{genome_name}\" -l /data/Modules/iv-backendV4/islandviewer/etc/logger.upload.conf 2>/dev/null"
    PIPELINE_PATH = "/data/Resources/MetaScheduler/pipeline"
    ANALYSIS_PATH = "/data/Modules/iv-backendV4/islandviewer/analysis/"
elif env.TEST_ENV:
    CUSTOM_GENOMES = "/data/Modules/iv-backendV4/islandviewer_dev/custom_genomes/"
    GENOME_UPLOAD_PATH = "/data/Modules/iv-backendV4/islandviewer_dev/custom_genomes/tmp/"
    GENOME_SUBMISSION_SCRIPT = "/data/Modules/iv-backendV4/islandviewer_dev/bin/submit_uploaded_genome.pl -c /data/Modules/iv-backendV4/islandviewer_dev/etc/islandviewer.config -f {filename} -n \"{genome_name}\" -l /data/Modules/iv-backendV4/islandviewer_dev/etc/logger.upload.conf 2>/dev/null"
    PIPELINE_PATH = "/data/Resources/MetaScheduler/pipeline"
    ANALYSIS_PATH = "/data/Modules/iv-backendV4/islandviewer_dev/analysis/"
else:
    CUSTOM_GENOMES = "/data/Modules/iv-backendV4/islandviewer_dev/custom_genomes/"
    GENOME_UPLOAD_PATH = "//data/Modules/iv-backendV4/islandviewer_dev/custom_genomes/tmp/"
    GENOME_SUBMISSION_SCRIPT = "/data/Modules/iv-backendV4/islandviewer_dev/bin/submit_uploaded_genome.pl -c /data/Modules/iv-backendV4/islandviewer_dev/etc/islandviewer.config -f {filename} -n \"{genome_name}\""
    PIPELINE_PATH = "/home/lairdm/workspace/metascheduler/pipelines"
    ANALYSIS_PATH = "/data/Modules/iv-backendV4/islandviewer_dev/analysis/"
