# celery configuration settings
# from celery.schedules import crontab
from datetime import timedelta

BROKER_URL = 'redis://localhost:6379/'
CELERY_RESULT_BACKEND = "redis"
CELERY_REDIS_HOST = "localhost"
CELERY_REDIS_PORT = 6379
CELERY_IMPORTS=("tasks")
 
CELERYBEAT_SCHEDULE = {
    'every-minute': {
        'task': 'tasks.test_task',
        'schedule': timedelta(minutes=15),
    },
}