"""delegacje URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
import delegacje
from setup.views import user_login
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from delegacje import app_config

urlpatterns = [
    path(app_config.LINK_PREFIX + 'admin/', admin.site.urls),
    path(app_config.LINK_PREFIX + 'e-delegacje/', include("e_delegacje.urls")),
    path(app_config.LINK_PREFIX + 'setup/', include("setup.urls")),
    path(app_config.LINK_PREFIX , user_login, name='login'),
    path(app_config.LINK_PREFIX + 'accounts/login/', user_login, name='login'),
    path(app_config.LINK_PREFIX + 'accounts/', include("django.contrib.auth.urls")),
]
urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
