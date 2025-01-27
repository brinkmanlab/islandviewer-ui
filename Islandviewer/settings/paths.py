import os
import sys
import env

PROJECT_PATH  = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_PATH)
sys.path.insert(0, os.path.join(BASE_DIR, "lib"))

if env.PROD_ENV:
    CUSTOM_GENOMES = "/mypath/islandviewerV4/data/custom_genomes/"
    GENOME_UPLOAD_PATH = "/mypath/islandviewerV4/data/custom_genomes/tmp/"
    GENOME_SUBMISSION_SCRIPT = "/mypath/islandviewerV4/static/bin/submit_uploaded_genome.pl -c /mypath/islandviewerV4/static/etc/islandviewer.config -f {filename} -n \"{genome_name}\" -l /mypath/islandviewerV4/static/etc/logger.upload.conf 2>/dev/null"
    PIPELINE_PATH = "/mypath/scheduler/metascheduler/static/etc/pipeline"
    ANALYSIS_PATH = "/mypath/islandviewerV4/data/analysis"
