#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from functools import wraps
from inspect import getmembers, ismethod

from bolibana_reporting.models.Options import Options


def reference(func):
    """ decorator adding _is_reference attribute """
    func._is_reference = True

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        return func(*args, **kwargs)
    return func


def label(label, is_sub=False):
    """ decorator adding a label string. Used for series/row names """
    def outer_wrapper(func, *args, **kwargs):
        func._label = label
        func._is_sub = is_sub

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)
        return func
    return outer_wrapper


def indicator(index=0, reference=None):
    """ indicator tagging as row with a reference row name """
    def outer_wrapper(func, *args, **kwargs):
        func._is_indicator = True
        func._reference = reference
        func._index = index

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            return func(*args, **kwargs)
        return func
    return outer_wrapper


class NoSourceData(Exception):
    """ Custom Exception to catch periods without Data """
    pass


class IndicatorTable(object):
    """ Data Table descriptor

        ARGUMENTS:
            - entity: Entity object
            - periods: list of Period objects """

    # options common to all subclasses
    # can be override.
    main_default_options = {'with_data': True, \
                            'with_total': False, \
                            'with_reference': True}

    # sub-class level default options
    default_options = {}

    def __init__(self, entity, periods, *args, **kwargs):
        self.entity = entity
        self.periods = periods
        self.setup(kwargs)

    def setup(self, options):
        """ prepares the self.options dict with all options found

            Options are composed of (in order):
            1. main_default_options dict
            2. default_options dict
            3. any keyword argument passed to constructor.
            Each pass overrides conflicting options """
        opt = self.main_default_options
        opt.update(self.default_options)
        opt.update(options)
        self.options = Options(**opt)

    def data_unsorted(self):
        """ builds the data dictionary. """
        _data = {}
        for line in self.get_lines():
            is_ref = self.line_is_ref(line)
            if (is_ref and self.options.with_reference) or not is_ref:
                _data[self.line_index_slug(line)] = self.get_line_data(line)
        return _data

    def data(self):
        """ access method: sorted data dictionary items """
        return sorted(self.data_unsorted().items())

    def line_is_ref(self, name):
        """ is the requested line a reference one ? """
        return hasattr(getattr(self, name), '_is_reference')

    def line_index_slug(self, name):
        """ sorting-safe index slug for a line """
        try:
            return '%s_%s' % (getattr(self, name)._index, name)
        except:
            return name

    def get_lines(self):
        """ list of lines to process """
        inspect_lambda = lambda x: ismethod(x) and hasattr(x, '_is_indicator')
        return [m[0] for m in getmembers(self, inspect_lambda)]

    def period_is_valid(self, period):
        """ [to override] is the current Period valid in terms of data ? """
        return True

    def get_line_data(self, name):
        """ build line data dictionary """
        # create stub dict for the line
        line_data = {'label': self.get_line_label(name), 'values': {}}

        # loop on periods (columns)
        for period in self.periods:

            # Periods might be invalid: no data for the period.
            # In that case, we'll just skip it.
            if not self.period_is_valid(period):
                # default empty period dict
                line_data['values'][period.pid] = {'value': None, \
                                                   'percent': None}
                continue

            # get the raw value for that period
            line_data['values'][period.pid] = \
                               {'value': self.get_indicator_data(name, period)}

            # calculate the percentage if required
            if self.options.with_percentage:
                line_data['values'][period.pid]['percent'] = \
                                          self.get_indicator_rate(name, period)

        # calculate total if required
        if self.options.with_total:
            line_data['total'] = \
                {'value': sum(self.clean_list([l['value'] \
                                    for l in line_data['values'].values()])), \
                 'percent': 1}

        return line_data

    def get_line_label(self, name):
        """ Label (row/series name) for a line """
        try:
            # label is store as property of the function using @label
            return getattr(self, name)._label
        except:
            return name

    @classmethod
    def clean_list(cls, alist):
        """ removes all occurences of None in the list """
        while True:
            try:
                alist.remove(None)
            except ValueError:
                break
        return alist

    def get_indicator_data(self, name, period):
        """ retrieve raw value for a line and a period """
        # get a list of all methods matching criteria:
        # indicator with correct name. There should be exactly one.
        inspect_lambda = lambda x: ismethod(x) \
                                and hasattr(x, '_is_indicator') \
                                and x.__name__ == name
        mms = getmembers(self, inspect_lambda)
        try:
            # call the actual function
            return mms[0][1](period)
        except NoSourceData:
            return None

    def get_indicator_rate(self, name, period):
        """ calculate percentage value for a line and a period """

        # return 100% is line is its reference one.
        if self.get_refname_for(name) == name:
            return 1

        # retrieve value of its reference
        ref = self.get_reference_value(name, period)
        # calculate raw value (we should be smarter here otherwise
        # we calculate it two times.
        value = self.get_indicator_data(name, period)

        # return None if there is no data value
        if value == None:
            return None

        try:
            # division of value / ref
            return float(value) / float(ref)
        except ZeroDivisionError:
            return 0

    def get_reference_value(self, name, period):
        """ value of the reference field for a line and period """
        # retrieve name of reference line
        ref_name = self.get_refname_for(name)
        # return raw value for that line/period
        return self.get_indicator_data(ref_name, period)

    def get_refname_for(self, name):
        """ name of reference line for a given one """
        stref = getattr(self, name)._reference
        if not stref:
            inspect_lambda = lambda x: ismethod(x) \
                                    and hasattr(x, '_is_reference')
            stref = getmembers(self, inspect_lambda)[0][0]
        return stref
