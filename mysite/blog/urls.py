# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^blogs/$', views.get_blogs),
    url(r'^detail/(\d+)/$', views.get_details, name='blog_get_detail')
    ]