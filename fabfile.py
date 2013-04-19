from fabric.api import *
from fabric.contrib.files import exists
import time

vars = {
    # 'tomcat_version': '6.0.36'
}

env.forward_agent = True
# env.key_filename = '~/.vagrant.d/insecure_private_key'

def dev():
    """ Use development server settings """
    servers = ['vagrant@127.0.0.1:2222']
    env.hosts = servers
    return servers

def prod():
    """ Use production server settings """
    servers = []
    env.hosts = servers
    return servers

def test():
    """ Use test server settings """
    servers = []
    env.hosts = servers
    return servers

def all():
    """ Use all servers """
    env.hosts = dev() + prod() + test()

def init():
    """ Initialize the geoportal application """
    # _install_dos2unix()
    # _run_celery_flower()

def _set_environment():
    run('')
    
def _install_dos2unix():
    run('sudo apt-get install dos2unix')
    
def run_test_fvs():
    run('/usr/local/apps/growth-yield-batch/scripts/fvs /usr/local/apps/growth-yield-batch/testdata/7029_CT60/')
    
def run_test_batch():
    run('/usr/local/apps/growth-yield-batch/scripts/fvsbatch --purge /usr/local/apps/growth-yield-batch/testdata/')
    