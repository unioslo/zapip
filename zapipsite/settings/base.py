"""
Django settings for zapip

https://docs.djangoproject.com/en/3.1/topics/settings/
https://docs.djangoproject.com/en/3.1/ref/settings/
"""

import os
from typing import List, Tuple, Optional, Dict

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "BWnHHzU5S1eYhXPxM9KNI2Ntax1xIpZMAyAyjWJnqvPGxJtNulDmAnWsXRfnFGcq"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS: List[str] = []


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
]

INSTALLED_APPS += [
    "zapip",
]

MIDDLEWARE = [
    "log_request_id.middleware.RequestIDMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# REST_FRAMEWORK = {
#     "DEFAULT_AUTHENTICATION_CLASSES": (
#         "rest_framework.authentication.TokenAuthentication",
#         "rest_framework.authentication.SessionAuthentication",
#     ),
#     "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
# }

ROOT_URLCONF = "zapipsite.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "zapipsite.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = False
USE_TZ = True
DATETIME_FORMAT = "c"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# STATICFILES_DIRS = [os.path.join(BASE_DIR, "..", "zapip", "frontend", "dist")]

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"
# STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Logging

# Log level for all loggers except Django
LOG_LEVEL = "INFO"
if DEBUG:
    LOG_LEVEL = "DEBUG"

# Override this to DEBUG locally for super verbose logging
DJANGO_LOG_LEVEL = "INFO"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_id": {"()": "log_request_id.filters.RequestIDFilter"}},
    "formatters": {
        # see full list of attributes here:
        # https://docs.python.org/3/library/logging.html#logrecord-attributes
        "verbose": {
            "format": "%(asctime)s [%(threadName)s] [%(levelname)s] [%(name)s] [%(request_id)s] %(message)s"
        },
    },
    "handlers": {
        "console": {
            "formatter": "verbose",
            "filters": ["request_id"],
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": DJANGO_LOG_LEVEL,
            "propagate": False,
        },
        "": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
        },
        "pika": {"handlers": ["console"], "level": "ERROR"},
    },
}


# Zapip

# For certain views, we want to validate that the request is coming from
# a proxy or API gateway. All headers (keys) must contain the configured
# value for the request to be let through.

# For easier local development: None disables header authentication.
# HEADER_AUTH: Optional[Dict[str, str]] = None

# For production: Require a header to be set.
# HEADER_AUTH: Optional[Dict[str, str]] = {
#     "X-Zapip-Api-Key": "fafafafa-fafa-fafa-fafa-fafafafafafa"
# }

# We expect the API gateway to add these headers to any forwarded requests.
# "API ID" identifies the API known to the gateway.
# "Application ID" identifies the application known to the gateway.
# "Subscription ID" identifies an instance of an application being granted
# access to an API. Any API keys are associated with a subscription.
GATEWAY_API_ID_HEADER = "X-Api"
GATEWAY_APPLICATION_ID_HEADER = "X-Api-Application"
GATEWAY_SUBSCRIPTION_ID_HEADER = "X-Api-Subscription"

# Zoom client
ZOOM_API_BASE_URL = "https://zoom.example.com/"
ZOOM_API_HEADERS = {"X-Gravitee-Api-Key": "foo"}

# Request ID headers
LOG_REQUEST_ID_HEADER = "HTTP_X_GRAVITEE_TRANSACTION_ID"
REQUEST_ID_RESPONSE_HEADER = "X-Zapip-Response-For"
