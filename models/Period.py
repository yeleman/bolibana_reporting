#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from datetime import datetime, date, timedelta

from django.db import models

from bolibana_reporting.utils import week_from_weeknum, next_month


class DayManager(models.Manager):
    def get_query_set(self):
        return super(DayManager, self).get_query_set() \
                                      .filter(period_type=Period.DAY)


class WeekManager(models.Manager):
    def get_query_set(self):
        return super(WeekManager, self).get_query_set() \
                                       .filter(period_type=Period.WEEK)


class MonthManager(models.Manager):
    def get_query_set(self):
        return super(MonthManager, self).get_query_set() \
                                        .filter(period_type=Period.MONTH)


class QuarterManager(models.Manager):
    def get_query_set(self):
        return super(QuarterManager, self).get_query_set() \
                                          .filter(period_type=Period.QUARTER)


class SemesterManager(models.Manager):
    def get_query_set(self):
        return super(SemesterManager, self).get_query_set() \
                                           .filter(period_type=Period.SEMESTER)


class YearManager(models.Manager):
    def get_query_set(self):
        return super(YearManager, self).get_query_set() \
                                       .filter(period_type=Period.YEAR)


class CustomManager(models.Manager):
    def get_query_set(self):
        return super(CustomManager, self).get_query_set() \
                                        .filter(period_type=Period.CUSTOM)


class Period(models.Model):
    ''' Represents a Period of time. Base class ; should not be used directly.

    Use DayPeriod, MonthPeriod, etc instead.
    Provides easy way to find/create period for reporting.

    p = MonthPeriod.find_create_from(2011, 3)
    p.next() '''

    class Meta:
        app_label = 'bolibana_reporting'
        unique_together = ('start_on', 'end_on', 'period_type')

    ONE_SECOND = 0.0001
    ONE_MICROSECOND = 0.00000000001

    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    QUARTER = 'quarter'
    SEMESTER = 'semester'
    YEAR = 'year'
    CUSTOM = 'custom'

    PERIOD_TYPES = (
        (DAY, u"Day"),
        (WEEK, u"Week"),
        (MONTH, u"Month"),
        (QUARTER, u"Quarter"),
        (SEMESTER, u"Semester"),
        (YEAR, u"Year"),
        (CUSTOM, u"Custom"),
    )

    start_on = models.DateTimeField()
    end_on = models.DateTimeField()
    period_type = models.CharField(max_length=15, \
                                   choices=PERIOD_TYPES, default=CUSTOM)

    objects = models.Manager()
    days = DayManager()
    weeks = WeekManager()
    months = MonthManager()
    quarters = QuarterManager()
    semesters = SemesterManager()
    years = YearManager()
    customs = CustomManager()
    django = models.Manager()

    @classmethod
    def type(cls):
        ''' default type for period creation '''
        return cls.CUSTOM

    @classmethod
    def delta(self):
        ''' timedelta() length of a period. 1 = one day. '''
        return 1 / 24

    def middle(self):
        ''' datetime at half of the period duration '''
        return self.start_on + ((self.end_on - self.start_on) / 2)

    def __unicode__(self):
        return self.name()

    def name(self):
        try:
            cls = eval(u"%sPeriod" % self.period_type.title())
            return cls.objects.get(id=self.id).name()
        except:
            return self.middle().strftime('%c')

    def next(self):
        ''' returns next period in time '''
        return self.find_create_by_date(self.middle() \
                                        + timedelta(self.delta()))

    @classmethod
    def boundaries(cls, date_obj):
        ''' start and end dates of a period from a date. '''
        start = date_obj - timedelta(cls.delta() / 2)
        end = start + self.delta()
        return (start, end)

    def includes(self, date_obj):
        ''' check if provided value is within this Period's scope

        date_obj can be:
         * datetime instance
         * date instance
         * integer (year) '''
        if isinstance(date, date_obj):
            date_obj = datetime(date.year, date.month, date.day, 12, 0)
        if isinstance(datetime, date_obj):
            return self.start_on < date_obj and self.end_on > date_obj
        elif isinstance(int, date_obj):
            pass
        return False
        # not sure what to do??
        raise ValueError("Can not understand date object.")

    @classmethod
    def find_create_from(cls, year, month=None, day=None, \
                         week=None, hour=None, minute=None, second=None):

        if not week and not month:
            # assume year search
            sy = datetime(year, 1, 1, 0, 0)
            ey = sy.replace(year=year + 1) - timedelta(ONE_MICROSECOND)
            try:
                period = cls.objects.filter(start_on__lte=sy, \
                                            end_on__gte=ey)[0]
            except IndexError:
                period = cls.find_create_with(sy, ey)
            return period

        if week:
            sw, ew = week_from_weeknum(year, week, is_iso=False)
            period = cls.find_create_with(sw, ew)
            return period

        month = month if month else 1
        day = day if day else 1
        hour = hour if hour else 0
        minute = minute if minute else 0
        second = second if second else 0

        date_obj = datetime(year, month, day, hour, minute, second)

        period = cls.find_create_by_date(date_obj)

        return period

    @classmethod
    def find_create_by_date(cls, date_obj):
        ''' creates a period to fit the provided date in '''
        try:
            period = [period for period in cls.objects.all() \
                                        if period.start_on <= date_obj \
                                        and period.end_on >= date_obj][0]
        except IndexError:
            period = cls.find_create_with(*cls.boundaries(date_obj))
            period.save()
        return period

    @classmethod
    def find_create_with(cls, start_on, end_on, period_type=None):
        ''' creates a period with defined start and end dates '''
        if not period_type:
            period_type = cls.type()
        try:
            period = cls.objects.get(start_on=start_on, \
                                     end_on=end_on, period_type=period_type)
        except cls.DoesNotExist:
            period = cls(start_on=start_on, end_on=end_on, \
                         period_type=period_type)
            period.save()
        return period


class DayPeriod(Period):

    class Meta:
        proxy = True
        app_label = 'bolibana_reporting'

    objects = DayManager()

    @classmethod
    def type(cls):
        return cls.DAY

    def name(self):
        return self.middle().strftime('%x')

    @classmethod
    def delta(self):
        return 1

    @classmethod
    def boundaries(cls, date_obj):
        start = date_obj.replace(hour=0, minute=0, \
                                 second=0, microsecond=0)
        end = start + timedelta(cls.delta()) - timedelta(ONE_MICROSECOND)
        return (start, end)


class MonthPeriod(Period):

    class Meta:
        proxy = True
        app_label = 'bolibana_reporting'

    objects = MonthManager()

    @classmethod
    def type(cls):
        return cls.MONTH

    def name(self):
        return u"%s" % self.middle().strftime('%m %Y')

    @classmethod
    def delta(self):
        return 28

    @classmethod
    def boundaries(cls, date_obj):
        nyear, nmonth = next_month(date_obj.year, date_obj.month)

        start = date_obj.replace(day=1, hour=0, minute=0, \
                                 second=0, microsecond=0)
        end = start.replace(year=nyear, month=nmonth) \
              - timedelta(cls.ONE_MICROSECOND)
        return (start, end)

class YearPeriod(Period):

    class Meta:
        proxy = True
        app_label = 'bolibana_reporting'

    objects = YearManager()

    @classmethod
    def type(cls):
        return cls.YEAR

    def name(self):
        return self.middle().strftime('%Y')

    @classmethod
    def delta(self):
        return 365

    @classmethod
    def boundaries(cls, date_obj):
        start = date_obj.replace(month=0, day=0, hour=0, minute=0, \
                                 second=0, microsecond=0)
        end = start + timedelta(cls.delta()) - timedelta(ONE_MICROSECOND)
        return (start, end)
