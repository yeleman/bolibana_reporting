#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

from bolibana_reporting.errors import ErrorManager


class DataValidator(object):

    errors = ErrorManager()

    def __init__(self, data_browser):
        self.data = data_browser

    def validate(self):
        pass

    def get(self, slug):
        return self.data.get(slug)

    def field_name(self, slug):
        return self.data.field_name(slug)
