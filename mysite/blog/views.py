# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from .models import BlogsPost
from django.shortcuts import render_to_response


def index(request):
    blog_list = BlogsPost.objects.all()
    return render_to_response('blog/index.html', {'blog_list': blog_list})