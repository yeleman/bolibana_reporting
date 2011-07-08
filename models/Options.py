#!/usr/bin/env python
# encoding=utf-8
# maintainer: rgaudin


class Options(dict, object):
    """ dict-like object allowing direct member access to its keys/values_list

        Example:
        adict = Options(name='madou', prof='student')
        a.name => 'madou'
        a.prof => 'student'
        a.age => None """

    def __init__(self, **kwargs):
        dict.__init__(self, **kwargs)

    def __getattribute__(self, name):
        # short-circuit object's internal members
        if name.startswith('_') or name in ('update'):
            return super(Options, self).__getattribute__(name)
        try:
            return self[name]
        except:
            return None

    def update(self, dic):
        # duplicate dict functionality
        for k, v in dic.items():
            setattr(self, k, v)
