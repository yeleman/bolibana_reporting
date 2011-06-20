#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from bolibana_reporting.errors import ErrorManager


class DataValidator(object):
    """ Interface for business-logic data validators """

    errors = ErrorManager()

    def __init__(self, data_browser):
        self.data = data_browser

    def validate(self):
        pass

    def get(self, slug):
        """ data for slug code """
        return self.data.get(slug)

    def field_name(self, slug):
        """ human-readable name representing slug """
        return self.data.field_name(slug)
