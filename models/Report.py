#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
import reversion

from bolibana_auth.models import *
from bolibana_reporting.models import Period


class ReportError(object):
    """ Single meaningful business-logic only error """
    def __init__(self):
        self.slug = ''
        self.type = ''

    def short(self):
        return u"Error on %s" % self.slug

    def concise(self):
        return "%s value is not valid" % self.slug

    def full(self):
        return "The value of the field %s is erroneous" % self.slug


class ReportErrorStack(object):
    """ Collection of ReportError for easy manipulation/forward to UI """

    def __init__(self):
        self.errors = []

    def short(self):
        return u"%d errors" % self.errors.__len__()

    def concise(self):
        return u"Errors on: %s" % u",".join(self.errors[:3])


class InvalidReportData(Exception):
    """ StandardException with a .stack property linking a ReportErrorStack """

    def __init__(self, message, stack):
        Exception.__init__(self, message)

        self.stack = stack


class Report(models.Model):

    STATUS_UNSAVED = 0
    STATUS_CREATED = 1
    STATUS_INCOMPLETE = 2
    STATUS_ERRONEOUS = 3
    STATUS_COMPLETE = 4
    STATUS_VALIDATED = 5
    STATUS_CLOSED = 6
    STATUSES = ((STATUS_UNSAVED, u"Unsaved"),
                (STATUS_CREATED, u"Created"),
                (STATUS_INCOMPLETE, u"Incomplete"),
                (STATUS_ERRONEOUS, u"Erroneous"),
                (STATUS_COMPLETE, u"Complete"),
                (STATUS_VALIDATED, u"Validated"),
                (STATUS_CLOSED, u"Closed"))

    TYPE_SOURCE = 0
    TYPE_AGGREGATED = 1
    TYPES = ((TYPE_SOURCE, u"Source"), (TYPE_AGGREGATED, u"Aggregated"))

    class Meta:
        app_label = 'bolibana_reporting'
        unique_together = ('period', 'entity', 'type')

    _status = models.PositiveIntegerField(choices=STATUSES, default=STATUS_CREATED)
    type = models.PositiveIntegerField(choices=TYPES)
    receipt = models.CharField(max_length=15, unique=True, blank=True, null=False)
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
        """ create a blank report filling all non-required fields """
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
    print "PRE SAVE"
    """ change _status property of Report on save() at creation """
    if instance._status == instance.STATUS_UNSAVED:
        instance._status = instance.STATUS_CLOSED
    if not instance.receipt:
        instance.receipt = u"%(day)d-REPORT_ID/%(location)d" \
                           % {'day': self.created_on.strftime('%j'), \
                              'location': self.entity.id}

@receiver(post_save, sender=Report)
def post_save_report(sender, instance, **kwargs):
    if 'REPORT_ID' in instance.receipt:
        instance.receipt = instance.receipt.replace('REPORT_ID', instance.id)
        instance.save()

