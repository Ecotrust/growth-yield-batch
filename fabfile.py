from fabric.api import *
from fabric.contrib.files import exists
from fabric.operations import run, put
import time
from fab_vars import *

env.forward_agent = True
env.key_filename = KEY_FILENAME


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


def stage():
    """ Use staging server settings """
    env.key_filename = AWS_KEY_FILENAME
    servers = [AWS_PUBLIC_DNS]
    env.hosts = servers
    return servers


def all():
    """ Use all servers """
    env.hosts = dev() + prod() + stage()


def init():
    """ Initialize the geoportal application """
    pass


def _set_environment():
    run('')


def run_test_fvs():
    run('/usr/local/bin/fvs /usr/local/apps/growth-yield-batch/testdata/varPN_rx25_cond42_site2/')


def run_test_batch():
    run('/usr/local/bin/fvsbatch --purge /usr/local/apps/growth-yield-batch/testdata/')


def run_test_buildkeys():
    import random
    import string
    tmpdir = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(10))
    run('/usr/local/bin/buildkeys /usr/local/apps/growth-yield-batch/test_build_keys/ /tmp/%s' % tmpdir)


def restart_services():
    """
    Not sure exactly why but puppet leaves the services in a bad state
    celeryd is not chdired to /var/celery and celeryflower doesnt pick up tasks.
    This is a band-aid to "fix" the issue
    """
    run('sudo service celeryd restart && sudo service supervisor stop && sudo service supervisor start')
    
def copy_fussy():
    run('sudo mkdir -p /usr/local/apps')
    run('sudo mkdir -p /usr/local/apps/growth-yield-batch')
    run('sudo mkdir -p /usr/local/apps/growth-yield-batch/fvsbin')
    run('sudo mkdir -p /usr/local/apps/growth-yield-batch/puppet')
    run('sudo mkdir -p /usr/local/apps/growth-yield-batch/scripts')
    run('sudo mkdir -p /usr/local/apps/growth-yield-batch/testdata')
    run('sudo chgrp -R ubuntu /usr/local/apps/growth-yield-batch')
    run('sudo chmod -R 775 /usr/local/apps/growth-yield-batch')
    run('sudo mkdir -p /tmp/vagrant-puppet')
    run('sudo mkdir -p /tmp/vagrant-puppet/manifests')
    run('sudo mkdir -p /tmp/vagrant-puppet/modules')
    run('sudo chgrp -R ubuntu /tmp/vagrant-puppet')
    run('sudo chmod -R 775 /tmp/vagrant-puppet')
    run('sudo mkdir -p /vagrant')
    run('sudo chgrp -R ubuntu /vagrant')
    run('sudo chmod -R 775 /vagrant')
    
    put('./fvsbin', '/usr/local/apps/growth-yield-batch/fvsbin')
    put('./puppet', '/usr/local/apps/growth-yield-batch/puppet')
    put('./scripts', '/usr/local/apps/growth-yield-batch/scripts')
    put('./testdata', '/usr/local/apps/growth-yield-batch/testdata')
    put('./requirements.txt', '/usr/local/apps/growth-yield-batch/')
    put('./puppet/manifests', '/tmp/vagrant-puppet/manifests')
    put('./puppet/modules', '/tmp/vagrant-puppet/modules')
    put('./requirements.txt', '/vagrant/requirements.txt')  #expected in puppet-script

    
def copy():
    run('sudo mkdir -p /usr/local/apps')
    run('sudo mkdir -p /usr/local/apps/growth-yield-batch')
    run('sudo chgrp -R ubuntu /usr/local/apps/growth-yield-batch')
    run('sudo chmod -R 775 /usr/local/apps/growth-yield-batch')
    run('sudo mkdir -p /vagrant')
    run('sudo chgrp -R ubuntu /vagrant')
    run('sudo chmod -R 775 /vagrant')
    
    put('./', '/usr/local/apps/growth-yield-batch/')
    put('./requirements.txt', '/vagrant/requirements.txt')  #expected in celery module
    
def install_puppet():
    run('sudo apt-get install puppet')
    
    #Copy in conf file /etc/puppet/puppet.conf
    put('puppet/puppet/manifests/*', '/etc/puppet/manifests/')
    put('puppet/puppet/modules/*', '/etc/puppet/modules/')
    
    # run('sudo puppet apply --modulepath=/usr/local/apps/growth-yield-batch/puppet/puppet/modules /usr/local/apps/growth-yield-batch/puppet/puppet/manifests/gybatch.pp')
    # run('sudo puppet apply --templatedir=/usr/local/apps/growth-yield-batch/puppet/puppet/manifests/files /usr/local/apps/growth-yield-batch/puppet/puppet/manifests/gybatch.pp')
    
    
def provision():
    # how to get modules?
    # run('puppet /usr/local/apps/growth-yield-batch/puppet/puppet/manifests/gybatch.pp')
    run('sudo puppet /etc/puppet/manifests/gybatch.pp')
    # getting references to group 'vagrant' - fixed only source I could find: growth-yield-batch\puppet\modules\python\manifests\venv\isolate.pp
    # -- found another in gybatch.pp
    # -- and another in celeryflower.conf
