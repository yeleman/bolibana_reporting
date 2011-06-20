#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.contrib import admin


class EntityAdmin(admin.ModelAdmin):

    list_filter = ('type', 'parent')
    ordering = ('slug',)
    search_fields = ('slug', 'name')


class EntityTypeAdmin(admin.ModelAdmin):

    pass


class Period(admin.ModelAdmin):

    pass


class MonthPeriod(admin.ModelAdmin):

    pass


class YearPeriod(admin.ModelAdmin):

    pass


class ReportAdmin(admin.ModelAdmin):

    pass
