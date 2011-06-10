#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

import os
import re

import xlrd


class MissingData(Exception):
    pass


class IncorrectReportData(Exception):
    pass


class ExcelTypeConverter(object):

    @classmethod
    def clean(cls, value):
        return unicode(value).strip()

    @classmethod
    def clean_str(cls, value):
        return unicode(value).strip().lower()

    @classmethod
    def ChoiceList(cls, value, choicelist):
        if value in choicelist:
            return value
        else:
            raise ValueError(u"%s not in %s" % (value, choicelist))

    @classmethod
    def LowerChoiceList(cls, value, choicelist):
        if cls.clean_str(value) in choicelist:
            return cls.clean_str(value)
        else:
            raise ValueError(u"%s not in %s" % (cls.clean_str(value), \
                                                choicelist))

    @classmethod
    def NormalizedChoiceList(cls, value, choicemap):
        if cls.clean_str(value) in choicemap:
            return choicemap[cls.clean_str(value)]
        else:
            raise ValueError(u"%s not in %s" % (cls.clean_str(value), \
                                                choicemap.keys()))

    @classmethod
    def NormalizedIntChoiceList(cls, value, choicelist):
        if int(value) in choicelist:
            return int(value)
        else:
            raise ValueError(u"%s not in %s" % (cls.clean_str(value), \
                                                choicelist))


class ExcelFormField(object):

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
        if self.name:
            return self.name
        return self.coord

    def convert_data(self, value):
        if not self.type:
            return value
        if self.cast_args:
            return self.type(value, self.cast_args)
        else:
            return self.type(value)


class ExcelErrorManager(object):

    def __init__(self):
        self.reset()

    def add(self, error, section=None):
        if section == None:
            section = 'default'
        # create section if it doesn't exist
        if not section in self.data:
            self.add_section(section)

        if not error in self.data[section]:
            return self.data[section].append(error)
        else:
            return False

    def add_section(self, section):
        if not section in self.data:
            self.data[section] = []

    def count(self):
        count = 0
        for value in self.data.values():
            count += value.__len__()
        return count

    def all(self, by_section=False):
        if by_section:
            array = {}
            for sid, section in self.data.items():
                if section.__len__() > 0:
                    array[sid] = section
            return array

        array = []
        for section in self.data.values():
            array.extend(section)
        return array

    def reset(self):
        self.data = {'default': []}


class ExcelForm(object):

    _mapping = None
    version = None
    data = {}

    def __init__(self, filepath, sheet=None, version=None):

        self.errors = ExcelErrorManager()

        if version:
            self.version = version

        self.filepath = filepath
        self.read(sheet)

    def read(self, sheet):
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
        except:
            raise
            self.errors.add(u"Impossible d'ouvrir le masque de saisie. " \
                            u"Le fichier est corrompu ou a été modifié.")

        for fieldid, field in self.mapping().items():
            self.map_field(field, fieldid)

    def mapping(self):
        if self.version:
            return self._mapping[version]
        else:
            return self._mapping[self._mapping.keys()[0]]

    def data_for_coord(self, coord):
        XLS_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        letter, line = re.match(r'([a-zA-Z]+)([0-9]+)', coord).groups()
        row = int(line) - 1
        column = XLS_LETTERS.index(letter.upper())
        return self.ws.row_values(row)[column]

    def field_name(self, variable):
        return self.mapping()[variable].display_name()

    def get(self, variable, silent=False):
        try:
            return self.data[variable]
        except KeyError:
            if silent:
                return None
            raise MissingData

    def set(self, variable, value):
        self.data[variable] = value

    def map_field(self, field, variable):
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
        self.errors.add("%s is not a valid data for %s" \
                        % (data, field.display_name()))

    def is_valid(self):
        # check completeness
        if self.is_complete():
            # check for errors
            self.validate()

        return self.errors.count() == 0

    def is_complete(self):
        return False

    def to_dict(self):
        return self.data
