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

    def display_name(self):
        return self.name.title()

    def display_full_name(self):
        return u"%(name)s/%(parent)s" % \
               {'name': self.display_name(), 'parent': self.parent.display_name()}

    def display_code_name(self):
        return u"%(code)s/%(name)s" % \
               {'code': self.slug, 'name': self.display_name()}
