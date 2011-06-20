#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.db import models
from django.utils.translation import ugettext_lazy as _, ugettext


class EntityType(models.Model):

    class Meta:
        app_label = 'bolibana_reporting'
        verbose_name = _(u"Entity Type")
        verbose_name_plural = _(u"Entity Types")

    name = models.CharField(_(u"Name"), max_length=30)
    slug = models.SlugField(_(u"Slug"), max_length=15, unique=True)

    def __unicode__(self):
        return self.name
