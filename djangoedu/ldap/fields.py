import ldap

from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings
from django.core import validators
from django import oldforms
from django.core.cache import cache

from djangoedu.ldap.utils import LDAPConnection, SecureLDAPConnection, LDAPItem

class LDAPObject(object):
    """LDAPObject that is returned when LDAPObjectField attribute is accessed."""
    
    def __init__(self, LDAPItem, orig_value):
        """Create a LDAPObject with the original value saved."""
        for attribute, values in LDAPItem.items():
            setattr(self, attribute, values)
        setattr(self, 'dn', LDAPItem.dn)
        setattr(self, '_orig_value', orig_value)
        #self._orig_value = orig_value

    def __unicode__(self):
        return u"%s" % self._orig_value
    
class LdapObjectField(models.Field):
    """This is a special field the stores a attribute for a LDAP object.
    
    It allows you access to the ldap properties for that object. For example
    consider the following model::
    
       class Person(models.Model):
           name = models.CharField(max_length=255)
           ldap = LdapObjectField(base="dc=directory,dc=State, dc=Edu", 
                                  server="ldap.state.edu", 
                                  port=389,
                                  filter_attr='uid')
    
    Then if you added a person to this class you could do the following 
    lookup::
    
        >>> person = Person.objects.get(pk=1)
        >>> person.ldap.givenName[0]
        'First_name'
    """
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, verbose_name=None, name=None, filter_attr=None, **kwargs):
        """Setup up ldap object field"""
        # if server/port are null use the defaults from settings.py
        self.base = kwargs.get('base') or getattr(settings, 'LDAP_BASE', '')
        self.server = kwargs.get('server') or getattr(settings, 'LDAP_SERVER', None)
        self.port = kwargs.get('port') or getattr(settings, 'LDAP_SERVER_PORT', 389)
        self.filter_attr = filter_attr
        assert(self.filter_attr, "Must provide a filter_attr")
        self.is_secure = getattr(settings, 'LDAP_SECURE_CONNECTION', False)
        self.username = getattr(settings, 'LDAP_SERVER_USER', '')
        self.password = getattr(settings, 'LDAP_SERVER_USER_PASSWORD', '')
        self.cache_timeout = getattr(settings, 'LDAP_CACHE_TIMEOUT', 43200) # 24 hours
        kwargs['max_length'] = kwargs.get('max_length', 255)
        models.Field.__init__(self, verbose_name, name, **kwargs)
    
    def get_manipulator_field_objs(self):
        return [oldforms.TextField]

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(LdapObjectField, self).formfield(**defaults)
    
    def to_python(self, value):
        """Lookup ldap object and return it."""
        if not value:
            return
        cache_key = '_'.join([self.server, self.filter_attr, value])
        cached = cache.get(cache_key)
        if cached:
            return cached
        l = {'port': self.port, 'user': self.username, 'password': self.password}
        if self.is_secure:
            connection = SecureLDAPConnection(self.server, **l)
        else:
            connection = LDAPConnection(self.server, **l)
        filter = "%s=%s" % (self.filter_attr, value)
        ldap_obj = connection.search(self.base, filter)
        if len(ldap_obj) != 1:
            raise validators.ValidationError, _("This filter must return a unique LDAP Object.")
        obj = LDAPObject(ldap_obj[0], value)
        cache.set(cache_key, obj, self.cache_timeout)
        return obj
    
    def get_db_prep_save(self, value):
        # Casts dates into string format for entry into database.
        if value is not None:
            value = value._orig_value
        return models.Field.get_db_prep_save(self, value)
