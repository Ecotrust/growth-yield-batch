from celery import Celery
import sys
from run_fvs import apply_fvs_to_plotdir

celery = Celery()
sys.path.append("/var/celery")
sys.path.append("/usr/local/apps/growth-yield-batch/scripts")
celery.config_from_object('celeryconfig')

@celery.task(max_retries=5, default_retry_delay=5)  # retry up to 5 times, 5 seconds apart
def fvs(plotdir):
    apply_fvs_to_plotdir(plotdir)  

