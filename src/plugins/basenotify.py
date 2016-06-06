import os
import dbus
from dbus.exceptions import DBusException

from ipapython.ipa_log_manager import root_logger

class OperationBase(object):
    """Base class for extending ipa's operations"""
    def __init__(self, service_name, object_path, interface, method=None):
        """
        Sets up attributes needed to connect to a remote object over dbus

        Arguments:
        service_name - name of the service connecting to
        object_path - path to a remote object exported by the service
        interface - interface of the remote object

        Optional arguments:
        method - name of the remote object's method to be callled
        """
        self._sn = service_name
        self._op = object_path
        self._if = interface
        self._method = method
        self._levels = { 0 : 'info',
                         1 : 'debug',
                         2 : 'warning',
                         3 : 'error',
                         4 : 'critical',
        }
    def log_message(self, level, msg):
        """
        Logs a message using ipa's root_logger

        Arguments:
        level - either log level id or log level name
        msg - string containing a message to be logged
        """
        if level in self._levels:
            log = getattr(root_logger, self._levels[level])
        elif level in self._levels.values():
            log = getattr(root_logger, level)
        else:
            # TODO: Unknown log level, log something?
            return
        log('notify: ' + msg)
    def _setup_dbus_dict(self, dn, entry_attrs=None, attrs_list=None):
        """
        Transforms ipapython's LDAPEntry object into a dbus Dictionary

        Arguments:
        dn - distinguished name of the LDAPEntry

        Optional arguments:
        entry_attrs - an LDAPEntry object
        attrs_list - list of all attributes intended to be fetched from the back end

        Returns a dbus dictionary with the dn attached
        """
        dbus_dict = { 'dn' : str(dn) }
        # Create string representations of ipapython's objects
        if entry_attrs:
            entry_attrs = dict(entry_attrs)
            for k,v in entry_attrs.items():
                    if isinstance(v, list):
                        for i, value in enumerate(v):
                            v[i] = str(value)
                        entry_attrs[k] = v
                    else:
                        entry_attrs[k] = str(v)
            dbus_dict['entry_attrs'] = dbus.Dictionary(entry_attrs,
                                                       signature='sv')
        # Add attributes to be fetched if available
        if attrs_list:
            for i, value in enumerate(attrs_list):
                attrs_list[i] = str(value)
            dbus_dict['attrs_list'] = attrs_list
        return dbus.Dictionary(dbus_dict, signature='sv')

    def _get_dbus_object(self, service_name, object_path):
        """
        Tries to connect to a remote service's object over dbus

        Arguments:
        service_name = Name of the service connecting to
        object_path = Path to the object to be returned

        Returns the remote object or None on error
        """
        try:
            bus = dbus.SystemBus()
            obj = bus.get_object(service_name, object_path)
        except DBusException as e:
            self.log_message('debug', str(e))
            obj = None
        return obj

    def _send_over_dbus(self, dbus_dict, remote_object, method_name):
        """
        Sends a dictionary over dbus to the specified remote object

        Arguments:
        dbus_dict - dictionary to be sent
        remote_object - recipient remote object
        method_name - name of the method to be called, either "pre" or "post"
        """
        if remote_object:
            method = getattr(remote_object, method_name)
            try:
                log_code, log_msg = method(dbus_dict, dbus_interface = self._if)
            except DBusException as e:
                error = str(e).strip().split('\n')[-1]
                self.log_message('debug', error)
            else:
                self.log_message(log_code, log_msg)

    def __call__(self, operation, ldap, dn, entry_attrs,
                    *keys, **options):
        dbus_dict = self._setup_dbus_dict(dn, entry_attrs)
        user_obj = self._get_dbus_object(self._sn, self._op)
        self._send_over_dbus(dbus_dict, user_obj, self._method)
        return dn

class PreOperation(OperationBase):
    def __init__(self, service_name, object_path, interface, method=None):
        method = 'pre'
        super(PreOperation, self).__init__(service_name, object_path, interface, method)

class PostOperation(OperationBase):
    def __init__(self, service_name, object_path, interface, method=None):
        method = 'post'
        super(PostOperation, self).__init__(service_name, object_path, interface, method)

class DeleteOperation(OperationBase):
    def __call__(self, operation, ldap, dn, *keys, **options):
        entry_attrs = None
        super(DeleteOperation, self).__call__(operation, ldap, dn,
                                              entry_attrs, *keys, **options)
        return dn
