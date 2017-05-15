# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, Http404
from .forms import CommentForm
# Create your views here.
from .models import *


def index(request):
    #blog_list = BlogsPost.objects.all()
    return render_to_response("hello this is my blog")


def get_blogs(request):
    blogs = Blog.objects.all().order_by("-created")
    return render_to_response('blog/blog_list.html', {'blogs': blogs})


def get_details(request, blog_id):
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        raise Http404
    if request.method == 'GET':
        form = CommentForm()
    else:
        form = CommentForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            cleaned_data['blog'] = blog
            Comment.objects.create(**cleaned_data)
    ctx = {
        'blog': blog,
        'comments': blog.comment_set.all().order_by('-created'),
        'form': form
    }
    return render(request, 'blog/blog_details.html', ctx)