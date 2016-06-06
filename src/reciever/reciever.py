import os
import time, datetime
import tempfile

from gi.repository import GLib

import dbus
import dbus.service
import dbus.mainloop.glib

tmp_name = 'ipa-notify'

def print_file():
    tmp = os.path.join(tempfile.gettempdir(), tmp_name)
    if os.path.exists(tmp):
        with open(tmp, 'r') as f:
            s = f.read()
        blocks = s.split('===')[:-1]
        d = {}
        for block in blocks:
            lines = block.split('\n')
            head = lines[0]
            print head
            body = '\n'.join(lines[1:])
            print body
            if head in d:
                d[head].append(body)
            else:
                d[head] = [body]
        print d
    return True

class RecieverBase(dbus.service.Object):
    def _save_to_file(self, header, dn, attrs=None):
        tmp = os.path.join(tempfile.gettempdir(), tmp_name)
        with open(tmp, 'a') as f:
            f.write(header + '\n')
            f.write(str(datetime.datetime.now()) + '\n')
            f.write('dn: ' + dn + '\n')
            for name, value in attrs:
                if isinstance(value, dbus.Array):
                    value = ', '.join(value)
                f.write('{}: {}\n'.format(str(name), str(value)))
            f.write('===')
        os.chmod(tmp, 0700)

class UserAdd(RecieverBase):
    @dbus.service.method('org.freeipa.notifications.user.added')
    def pre(self, entry_dict):
        print 'User-Add - Pre: ' + entry_dict['dn']
        return (0, 'UserAdd Pre-operation')

    @dbus.service.method('org.freeipa.notifications.user.added')
    def post(self, entry_dict):
        attrs = [(key, value) for key, value in entry_dict['entry_attrs'].items()]
        self._save_to_file('User added', entry_dict['dn'], attrs)
        print 'User-Add - Post: ' + entry_dict['dn']
        return (0, 'UserAdd Post-operation')

class UserMod(RecieverBase):
    @dbus.service.method('org.freeipa.notifications.user.modified')
    def pre(self, entry_dict):
        print 'User-Mod - Pre: ' + entry_dict['dn']
        print 'User-Mod - Pre: ' + str(entry_dict['entry_attrs'])
        return (0, 'UserMod Pre-operation')

    @dbus.service.method('org.freeipa.notifications.user.modified')
    def post(self, entry_dict):
        print 'User-Mod - Post: ' + entry_dict['dn']
        print 'User-Mod - Post: ' + str(entry_dict['entry_attrs'])
        return (0, 'UserMod Post-operation')

class UserDel(RecieverBase):
    @dbus.service.method('org.freeipa.notifications.user.removed')
    def pre(self, entry_dict):
        print 'User-Del - Pre: ' + entry_dict['dn']
        return (0, 'UserDel Pre-operation')

    @dbus.service.method('org.freeipa.notifications.user.removed')
    def post(self, entry_dict):
        #self._save_to_file('User removed', entry_dict['dn'])
        print 'User-Del - Post: ' + entry_dict['dn']
        return (0, 'UserDel Post-operation')

if __name__ == '__main__':
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()
    name = dbus.service.BusName('org.freeipa.notifications', bus)
    user_add = UserAdd(bus, '/UserAdded')
    user_mod = UserMod(bus, '/UserModified')
    user_del = UserDel(bus, '/UserRemoved')

    mainloop = GLib.MainLoop()
    #GLib.timeout_add(6000, print_file)
    print 'Running FreeIPA notification reciever'
    mainloop.run()
