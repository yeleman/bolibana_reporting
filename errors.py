#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin

class MissingData(Exception):
    pass


class IncorrectReportData(Exception):
    pass


class ErrorManager(object):

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

    def fusion(self, error_manager):
        for section, errors in error_manager.all(True).items():
            for error in errors:
                self.add(error, section)
