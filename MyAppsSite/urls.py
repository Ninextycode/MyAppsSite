"""MyAppsSite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

import DjangoBacktester.views
import DjangoStega.views
import DjangoNNetEvolution.views

urlpatterns = [
    url(r'^admin/', admin.site.urls, name="admin"),
    url(r'^backtester/$',
        DjangoBacktester.views.write_form, name="write_form"),
    url(r'^backtester/evaluate/$',
        DjangoBacktester.views.evaluate_strategy, name="evaluate"),
    url(r'^backtester/get_shares_graphs/$',
        DjangoBacktester.views.get_shares_graphs, name="get_image"),

    url(r'^stega/$', DjangoStega.views.encoderedirect),
    url(r'^stega/encode/$', DjangoStega.views.encodeview , name='encode'),
    url(r'^stega/dencode/$', DjangoStega.views.decodeview, name='decode'),

    url(r'^nnevolution/$', DjangoNNetEvolution.views.main_view, name='evolution')
]
