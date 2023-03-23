#!C:/Users/LENOVO/Envs/meiduo_mall/Scripts python

import sys
sys.path.insert(0, '../')

import os
if not os.getenv('DJANGO_SETTINGS_MODULE'):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'meiduo_mall.settings.dev'