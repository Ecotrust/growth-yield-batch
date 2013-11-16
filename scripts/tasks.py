from celery import Celery
import sys
from run_fvs import apply_fvs_to_plotdir

celery = Celery()
sys.path.append("/var/celery")
sys.path.append("/usr/local/apps/growth-yield-batch/scripts")
celery.config_from_object('celeryconfig')

@celery.task
def fvs(plotdir):
    # TODO specify extract_methods=['csv'] if sqlite write locks become an issue
    apply_fvs_to_plotdir(plotdir)  

