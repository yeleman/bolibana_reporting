#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import os
import re
import logging

import xlrd
from django.utils.translation import ugettext as _

from bolibana_reporting.errors import (ErrorManager, MissingData, \
                                       IncorrectReportData)

logger = logging.getLogger(__name__)


class ExcelTypeConverter(object):
    """ module-like class offering different excel data to python mapping """

    @classmethod
    def clean(cls, value):
        """ a stripped unicode """
        return unicode(value).strip()

    @classmethod
    def clean_str(cls, value):
        """ lowercased stripped unicode """
        return unicode(value).strip().lower()

    @classmethod
    def ChoiceList(cls, value, choicelist):
        """ value if included in provided list """
        if value in choicelist:
            return value
        else:
            raise ValueError(u"%s not in %s" % (value, choicelist))

    @classmethod
    def LowerChoiceList(cls, value, choicelist):
        """ cleaned value if it is included in provided list """
        if cls.clean_str(value) in choicelist:
            return cls.clean_str(value)
        else:
            raise ValueError(u"%s not in %s" % (cls.clean_str(value), \
                                                choicelist))

    @classmethod
    def NormalizedChoiceList(cls, value, choicemap):
        """ mapped value of a cleaned index in a provided dict """
        if cls.clean_str(value) in choicemap:
            return choicemap[cls.clean_str(value)]
        else:
            raise ValueError(u"%s not in %s" % (cls.clean_str(value), \
                                                choicemap.keys()))

    @classmethod
    def NormalizedIntChoiceList(cls, value, choicelist):
        """ int value if it is included in provided list of int """
        if int(value) in choicelist:
            return int(value)
        else:
            raise ValueError(u"%s not in %s" % (cls.clean_str(value), \
                                                choicelist))


class ExcelFormField(object):
    """ A field in an Excel form represented by its coordinates """

    def __init__(self, coord, type=None, name=None, \
                 cast_args=None, attr=None, *args, **kwargs):
        self.coord = coord
        self.type = type
        self.name = name
        self.attr = attr
        self.cast_args = cast_args
        self.args = args
        self.kwargs = kwargs

    def display_name(self):
        """ name of the field """
        if self.name:
            return self.name
        return self.coord

    def convert_data(self, value):
        """ converted data from type property """
        if not self.type:
            return value
        if self.cast_args:
            return self.type(value, self.cast_args)
        else:
            return self.type(value)


class ExcelForm(object):

    """ A Form in an Excel File """

    _mapping = {None: {}}
    version = None
    data = {}

    def __init__(self, filepath, sheet=None, version=None):

        self.errors = ErrorManager()

        if version:
            self.version = version

        self.filepath = filepath
        self.sheet = sheet
        self.read()

    def read(self, sheet=None):
        """ parses all fields in mapping and stores converted data """
        if not sheet:
            sheet = self.sheet

        # one can re-call read() at any time
        self.errors.reset()

        try:
            book = xlrd.open_workbook(self.filepath)
            if isinstance(sheet, basestring):
                self.ws = book.sheet_by_name(sheet)
            elif isinstance(sheet, int):
                self.ws = book.sheets()[sheet]
            else:
                self.ws = book.sheets()[0]
        except Exception as e:
            logger.warning(u"Unable to read Excel Uploaded file %(path)s. " \
                           "Raised %(e)r" % {'path': self.filepath, 'e': e})
            self.errors.add(u"Impossible d'ouvrir le masque de saisie. " \
                            u"Le fichier est corrompu ou a été modifié.")
            return

        for fieldid, field in self.mapping().items():
            self.map_field(field, fieldid)

    def mapping(self):
        """ dict mapping of the current version """
        if self.version:
            return self._mapping[version]
        else:
            return self._mapping[self._mapping.keys()[0]]

    def data_for_coord(self, coord):
        """ raw data from Excel coordinates """
        XLS_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        letter, line = re.match(r'([a-zA-Z]+)([0-9]+)', coord).groups()
        row = int(line) - 1
        column = XLS_LETTERS.index(letter.upper())
        return self.ws.row_values(row)[column]

    def field_name(self, variable):
        """ name of field from slug """
        return self.mapping()[variable].display_name()

    def get(self, variable, silent=False):
        """ value of field from slug. Silent returns None instaed of raise """
        try:
            return self.data[variable]
        except KeyError:
            if silent:
                return None
            raise MissingData

    def set(self, variable, value):
        """ store value for that slug variable """
        self.data[variable] = value

    def map_field(self, field, variable):
        """ retrieve and store data from excel to mapping for field+slug """
        # raw data
        fdata = self.data_for_coord(field.coord)
        try:
            self.set(variable, field.convert_data(fdata))
        except ValueError as e:
            # field is blank
            if ExcelTypeConverter.clean_str(fdata).__len__() == 0:
                self.set(variable, None)
            else:
                self.value_error(fdata, field, variable, e)

    def value_error(self, data, field, variable, exception):
        """ adds an error if data is not valid """
        self.errors.add(_("%(data)s is not a valid data for %(field)s") \
                        % {'data': data, 'field': field.display_name()})

    def is_valid(self, *args, **kwargs):
        """ [override] complete with no errors ? """
        # check completeness
        if self.is_complete(*args, **kwargs):
            # check for errors
            self.validate(*args, **kwargs)

        return self.errors.count() == 0

    def is_complete(self, *args, **kwargs):
        """ [override] required fields filled? """
        return False

    def to_dict(self):
        """ raw dict of all data """
        return self.data
