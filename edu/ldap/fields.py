import ldap

from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings
from django.core import validators
from django import oldforms

from edu.ldap.utils import LDAPConnection, SecureLDAPConnection, LDAPItem

class LDAPObject(object):
    """LDAPObject that is returned when LDAPObjectField attribute is accessed."""
    
    def __init__(self, LDAPItem, orig_value):
        """Create a LDAPObject with the original value saved."""
        self._ldap_item = LDAPItem
        self._orig_value = orig_value
        
    def __getattr__(self, attribute):
        return self._ldap_item.__getattr__(attribute)

    def __getitem__(self, attribute):
        return self._ldap_item.__getitem__(attribute)

    def get(self, attribute, default=None):
        return self.__getitem__(attribute) or default
        
    def __unicode__(self):
        return u"%s" % self._orig_value
    
    def all(self):
        return unicode(self._ldap_item)

class LdapObjectField(models.Field):
    """This is a special field the stores a DN which relates to a LDAP object.
    
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
    
        >>> person = Person.objects.all()[0]
        >>> person.ldap.givenName 
        'FirstName'
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
        #TODO: cache this method
        if self.is_secure:
            connection = SecureLDAPConnection(self.server, port=self.port,
                                              user=self.username,
                                              password=self.password)
        else:
            connection = LDAPConnection(self.server, port=self.port,
                                        user=self.username,
                                        password=self.password)
        filter = "%s=%s" % (self.filter_attr, value)
        ldap_obj = connection.search(self.base, filter)
        if len(ldap_obj) != 1:
            raise validators.ValidationError, _("This filter must return a unique LDAP Object.")
        return LDAPObject(ldap_obj[0], value)
    
    def get_db_prep_save(self, value):
        # Casts dates into string format for entry into database.
        if value is not None:
            value = value._orig_value
        return models.Field.get_db_prep_save(self, value)
