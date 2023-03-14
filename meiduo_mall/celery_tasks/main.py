import os
from celery import Celery

if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ["DJANGO_SETTINGS_MODULE"] = "meiduo_mall.settings.dev"

celery_app = Celery('meiduo')

celery_app.config_from_object('celery_tasks.config')

# 注册任务
celery_app.autodiscover_tasks(['celery_tasks.sms', 'celery_tasks.email'])
