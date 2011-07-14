#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.contrib import admin


class EntityAdmin(admin.ModelAdmin):

    list_display = ('slug', 'name', 'type', 'parent', 'parent_level')
    list_filter = ('type', 'parent')
    ordering = ('slug',)
    search_fields = ('slug', 'name')


class EntityTypeAdmin(admin.ModelAdmin):

    pass


class PeriodAdmin(admin.ModelAdmin):

    pass


class MonthPeriodAdmin(admin.ModelAdmin):

    pass


class YearPeriodAdmin(admin.ModelAdmin):

    pass


class ReportAdmin(admin.ModelAdmin):

    pass
