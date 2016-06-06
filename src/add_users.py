"""
Useful testing functions that can be used with 'ipa console'
"""

import datetime
import numpy

def add_user():
    api.Command['user_add'](givenname=u'Sergej', sn=u'Sergejov', uid=u'usert')

def remove_user():
    api.Command['user_del'](uid=u'usert')

def test_user_plugin():
    add_user()
    remove_user()

def add_users():
    for i in range(0,10):
        api.Command['user_add'](givenname=u'Sergej', sn=u'Sergejov', uid=u'user'+str(i))

def remove_users():
    for i in range(0,10):
        api.Command['user_del'](uid=u'user'+str(i))
