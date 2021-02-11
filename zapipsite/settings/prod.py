import os

from .base import *

# This is the default configuration file when starting the app through zapip.wsgi.application
# Put secret production settings in local.py

DEBUG = False

# Email
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = os.getenv('EMAIL_HOST', 'mx.example.com')

# Security
# https://docs.djangoproject.com/en/3.1/topics/security/#ssl-https
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", default="").split(",")
    if os.getenv("ALLOWED_HOSTS")
    else []
)


try:
    from .local import *
except ImportError:
    pass
