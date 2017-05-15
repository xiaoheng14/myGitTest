# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import BlogsPost, BlogsPostAdmin
# Register your models here.

#admin.site.register(BlogsPost)
admin.site.register(BlogsPost, BlogsPostAdmin)
