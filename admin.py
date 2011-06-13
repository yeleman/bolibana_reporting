#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.contrib import admin


class EntityAdmin(admin.ModelAdmin):

    list_filter    = ('type', 'parent')
    ordering       = ('slug',)
    search_fields  = ('slug','name')
