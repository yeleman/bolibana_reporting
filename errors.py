#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin


class MissingData(Exception):
    """ A data/field which is expected to be field but is blank """
    pass


class IncorrectReportData(Exception):
    """ A data which is invalidated by business logic """
    pass


class ErrorManager(object):
    """ An interface to a category-sorted dictionnary of errors """

    def __init__(self):
        self.reset()

    def add(self, error, section=None):
        """ Add an error message to the specified category or default

            Categories are automatically created if missing """
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
        """ Add a category """
        if not section in self.data:
            self.data[section] = []

    def count(self):
        """ total number of errors in all categories """
        count = 0
        for value in self.data.values():
            count += value.__len__()
        return count

    def all(self, by_section=False):
        """ Array of messages if by_section provided otherwise a dict """
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
        """ removes all error messages and categories """
        self.data = {'default': []}

    def fusion(self, error_manager):
        """ fusion error messages & catgories from another Manager """
        for section, errors in error_manager.all(True).items():
            for error in errors:
                self.add(error, section)
