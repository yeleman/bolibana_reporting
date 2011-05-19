#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from mptt.models import MPTTModel, TreeForeignKey


class Entity(MPTTModel):

    class Meta:
        app_label = 'bolibana_reporting'

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=15, unique=True)
    type = models.ForeignKey('EntityType', related_name='entities')
    parent = TreeForeignKey('self', null=True, blank=True, \
                                                       related_name='children')

    def __unicode__(self):
        return self.name
