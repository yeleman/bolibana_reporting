#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_save, post_save

from bolibana_auth.models import *
from bolibana_reporting.models import Period


class ReportError(object):
    def __init__(self):
        self.slug = ''

    def short(self):
        return u"Error on %s" % self.slug

    def concise(self):
        return "%s value is not valid" % self.slug

    def full(self):
        return "The value of the field %s is erroneous" % self.slug


class ReportErrorStack(object):

    def __init__(self):
        self.errors = []

    def short(self):
        return u"%d errors" % self.errors.__len__()

    def concise(self):
        return u"Errors on: %s" % u",".join(self.errors[:3])


class Report(models.Model):

    STATUS_UNSAVED = 0
    STATUS_CREATED = 1
    STATUS_INCOMPLETE = 2
    STATUS_ERRONEOUS = 3
    STATUS_COMPLETE = 4
    # validated?
    STATUS_CLOSED = 5
    STATUSES = ((STATUS_UNSAVED, u"Unsaved"),
                (STATUS_CREATED, u"Created"),
                (STATUS_INCOMPLETE, u"Incomplete"),
                (STATUS_ERRONEOUS, u"Erroneous"),
                (STATUS_COMPLETE, u"Complete"),
                (STATUS_CLOSED, u"Closed"))

    class Meta:
        app_label = 'bolibana_reporting'
        unique_together = ('period', 'entity')

    _status = models.CharField(max_length=1, choices=STATUSES)
    receipt = models.CharField(max_length=15, null=True, blank=True)
    period = models.ForeignKey('Period', related_name='reports')
    entity = models.ForeignKey('Entity', related_name='reports')
    created_by = models.ForeignKey('bolibana_auth.Provider', \
                                   related_name='reports')
    created_on = models.DateTimeField(auto_now_add=True)
    modified_by = models.ForeignKey('bolibana_auth.Provider', \
                                    null=True, blank=True)
    modified_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return u"%(entity)s/%(period)s" % {'entity': self.entity, \
                                           'period': self.period}

    @classmethod
    def create(cls, period, entity, author, *args, **kwargs):
        report = cls(period=period, entity=entity, created_by=author, \
                     modified_by=author, _status=cls.STATUS_UNSAVED)
        for arg, value in kwargs.items():
            try:
                setattr(report, arg, value)
            except AttributeError:
                pass
        report.save()

    def validate(self):
        pass

    def status(self):
        return self._status


@receiver(pre_save, sender=Report)
def pre_save_report(sender, instance, **kwargs):
    """ change _status property of Report on save() at creation """
    if instance._status == instance.STATUS_UNSAVED:
        instance._status = instance.STATUS_CREATED


class ReportPart(models.Model):

    STATUS_UNSAVED = 0
    STATUS_CREATED = 1
    STATUS_INCOMPLETE = 2
    STATUS_ERRONEOUS = 3
    STATUS_COMPLETE = 4
    # validated?
    STATUS_CLOSED = 5
    STATUSES = ((STATUS_UNSAVED, u"Unsaved"),
                (STATUS_CREATED, u"Created"),
                (STATUS_INCOMPLETE, u"Incomplete"),
                (STATUS_ERRONEOUS, u"Erroneous"),
                (STATUS_COMPLETE, u"Complete"),
                (STATUS_CLOSED, u"Closed"))

    class Meta:
        app_label = 'bolibana_reporting'

    #_status = models.CharField(max_length=1, choices=STATUSES)
    report = models.ForeignKey('Report', related_name='+', \
                               null=True, blank=True)

    def __unicode__(self):
        if self.report:
            return u"Part/%s" % self.report.__unicode__()
        else:
            return u"Part/unattached"
