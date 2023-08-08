"""profilit_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='profilit-home'),
    path('about', views.about, name='profilit-about'),
    path('exploration', views.exploration, name='profilit-exploration'),
    path('transform', views.transform, name='profilit-transform'),
    path('match', views.match, name='profilit-match'),
    path('rules', views.rules, name='profilit-rules'),
    path('data', views.data, name='profilit-data'),
    #path('UIRules', views.highlight_duplicates, name='profilit-UIRules'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
