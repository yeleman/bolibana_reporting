#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models


class EntityType(models.Model):

    class Meta:
        app_label = 'bolibana_reporting'

    name = models.CharField(max_length=30)
    slug = models.SlugField(max_length=15, unique=True)

    def __unicode__(self):
        return self.name
