from fabric.api import *
from fab_vars import *

env.forward_agent = True
env.key_filename = KEY_FILENAME

servers = ['vagrant@127.0.0.1:2222']
#servers = ['ubuntu@ford.ecotrust.org']
env.hosts = servers
#env.key_filename = AWS_KEY_FILENAME_PROD

def restart_services():
    """
    Not sure exactly why but puppet leaves the services in a bad state
    celeryd is not chdired to /var/celery and celeryflower doesnt pick up tasks.
    This is a band-aid to "fix" the issue
    """
    run('sudo service celeryd restart && sudo supervisorctl restart all')
    run('sudo service nginx restart')


# def progress():
#     run('date')
#     run('find /usr/local/data/out/ -name "*.csv" | wc -l')
#     run('find /usr/local/data/out/ -name "*.err" | wc -l')
#     run('du -h /usr/local/data/out/ --max-depth=0')
