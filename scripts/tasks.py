from celery import Celery
import sys
import time
import random

celery = Celery()
sys.path.append("/var/celery")
celery.config_from_object('celeryconfig')


@celery.task
def add(x, y):
    time.sleep(random.randint(0, 4))
    return x + y


@celery.task
def square(z):
    time.sleep(random.randint(0, 4))
    return z ** 2


@celery.task
def fvs(datadir):
    print "Starting 'fvs %s'" % datadir
    time.sleep(random.randint(10, 25))
    print "Stopping 'fvs %s'" % datadir
    return True
