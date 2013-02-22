BROKER_URL = 'redis://<%= broker_host %>:<%= broker_port %>/<%= redis_broker_db %>'
BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': <%= redis_vis_timeout %>}
CELERY_RESULT_BACKEND = 'redis://<%= broker_host %>:<%= broker_port %>/<%= redis_results_db %>'
CELERY_DISABLE_RATE_LIMITS = True
CELERY_IMPORTS=("tasks",)  # look for a /var/celery/tasks.py
