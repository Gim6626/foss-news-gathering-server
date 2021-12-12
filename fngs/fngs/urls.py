"""fngs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

import auth.urls
import gatherer.urls
import gatherer.urls_v2
import search.urls
import osfriday.urls
import tbot.urls
import tbot.urls_v2

api_v1_prefix = 'api/v1/'
api_v2_prefix = 'api/v2'

urlpatterns = [
    path(f'{api_v2_prefix}/auth/', include(auth.urls)),
    path('admin/', admin.site.urls),
    path(f'{api_v2_prefix}/gatherer/', include(gatherer.urls_v2)),
    path(f'{api_v2_prefix}/tbot/', include(tbot.urls_v2)),
    path('', include(search.urls)),
    path('', include(osfriday.urls)),
]
urlpatterns += staticfiles_urlpatterns()
