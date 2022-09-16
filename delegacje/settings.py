"""
Django settings for delegacje project.

Generated by 'django-admin startproject' using Django 3.1.7.

For more information on this file, see
https://docs.djangoproject.com/en/3.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

""" Wersja testowa aplikacji
"""

import os
from pathlib import Path
from delegacje import app_config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = app_config.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False
# DEBUG = True

ALLOWED_HOSTS = app_config.ALLOWED_HOSTS

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'e_delegacje',
    'setup',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'delegacje.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'delegacje.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = app_config.DATABASES
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12, }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'delegacje.validators.NumberValidator'
    },
    {
        'NAME': 'delegacje.validators.UppercaseValidator'
    },
    {
        'NAME': 'delegacje.validators.LowercaseValidator'
    },
    {
        'NAME': 'delegacje.validators.SymbolValidator'
    },
]
LOGIN_URL = '/' + app_config.LINK_PREFIX + 'accounts/login/'


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True
""" jeśli ma działać na serwerze IIS użyj /prod/static/
    Jeśli ma działać na localhost użyj /static/
"""
STATIC_URL = app_config.STATIC_URL
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = app_config.MEDIA_URL

#  Email sending settings
EMAIL_HOST = app_config.EMAIL_HOST
EMAIL_HOST_USER = app_config.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = app_config.EMAIL_HOST_PASSWORD
EMAIL_PORT = app_config.EMAIL_PORT
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

AUTH_USER_MODEL = "setup.BtUser"
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGGING = {
    'version': 1,
    'loggers':{
        'django': {
            'handlers':['file'],
            'level':'DEBUG',
        }
    },
    'handlers':{
        'file':{
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename':'.\logs\debug2.log',
            'formatter': 'simpleRe'
        }
    },
    'formatters':{
        'simpleRe':{
            'format': '{levelname} {asctime} {process:d} {message} ',
            'style': '{'
        }
    },
}

# HTTPS settings
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_SECURE = True

SECURE_SSL_REDIRECT = True

# HSTS Settings
SECURE_HSTS_SECONDS = 60

SECURE_HSTS_INCLUDE_SUBDOMAINS = True

SECURE_HSTS_PRELOAD = True