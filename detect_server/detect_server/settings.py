# -*- coding: utf-8 -*-

"""
Django settings for detect_server project.

Generated by 'django-admin startproject' using Django 1.8.7.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import cPickle as pickle
import sys


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '5wl-j0*#d(07s&+x2-cn2y6u-@!ckih=3c=@dvo#cnr#8z#d7g'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'detect_app',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'detect_server.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'detect_server.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

MEDIA_URL="/media/"  
MEDIA_ROOT=os.path.join(BASE_DIR, "media")  
MAX_FILE_SIZE = 104857600

# projPath = '/Users/lujianyun/mytest/bishe/MobiSentry-master/'
projPath = '/Users/lujianyun/mytest/bishe/'

#init datas
clf_tags = [
    'LGBM', 
    'Ada',
    'RF',
    'SVM',
    'GBC',
    # 'KNN'
    ]

CLF_MAP = {}
#lightgbm

for tag in clf_tags:
    model_path = projPath
    if projPath.endswith('/bishe/'):
        model_path = projPath + 'final_models/'
    '''
    YOU SHOULD LOAD MODEL HERE
    '''
    clf = pickle.load( open( model_path + "/train_data_" + tag + ".p", "rb" ) )
    print(tag + ' model load completed')
    CLF_MAP[tag] = clf
#print('KNN' + ' model load completed') #TRICK
DATA = []
neighbor_result = pickle.load( open(projPath + '2rd_neighbor_result.p', "rb" ))
# print('neighbor_result' + ' load completed')

data_list = pickle.load( open(projPath + '2rd_data_list.p', "rb" ))
# print('data_list' + ' load completed')

DATA.append(neighbor_result)
DATA.append(data_list)









