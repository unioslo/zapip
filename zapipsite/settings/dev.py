from .base import *

# This is the default configuration file when running manage.py

ALLOWED_HOSTS += ["localhost", "127.0.0.1"]

try:
    from .local import *
except ImportError:
    pass
