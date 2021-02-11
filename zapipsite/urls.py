from django.contrib import admin
# from django.contrib.auth import urls as auth_urls
from django.urls import path, re_path, include

import os

from zapip import urls as zapip_urls

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(zapip_urls.urlpatterns)),
]
