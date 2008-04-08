import ldap

from django.db import models
from django.conf import settings

from edu.ldap.utils import LDAPConnection, SecureLDAPConnection

class LdapObjectField(models.Field):
    """This is a special field the stores a DN which relates to a LDAP object.
    
    It allows you access to the ldap properties for that object. For example
    consider the following model::
    
       class Person(models.Model):
           name = models.CharField(max_length=255)
           ldap = LdapObjectField(base="dc=directory,dc=State, dc=Edu", 
                                  server="ldap.state.edu", port=389)
    
    Then if you added a person to this class you could do the following 
    lookup::
    
        >>> person = Person.objects.all()[0]
        >>> person.ldap.givenName 
        'FirstName'
    """
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, base=None, server=None, port=None):
        """Setup up ldap object field"""
        # if server/port are null use the defaults from settings.py
        self.base = base or getattr(settings, 'LDAP_BASE', '')
        self.server = server or getattr(settings, 'LDAP_SERVER', None)
        self.port = port or getattr(settings, 'LDAP_SERVER_PORT', 389)
        self.is_secure = getattr(settings, 'LDAP_SECURE_CONNECTION', False)
        self.username = getattr(settings, 'LDAP_SERVER_USER', '')
        self.password = getattr(settings, 'LDAP_SERVER_USER_PASSWORD', '')
        return super(LdapObjectField, self).__init__()
    
    def db_type(self):
        return 'varchar(255)'
    
    def to_python(self, value):
        """Lookup ldap object and return it."""
        if self.is_secure:
            connection = SecureLDAPConnection(self.server, port=self.port,
                                              user=self.username,
                                              password=self.password)
        else:
            connection = LDAPConnection(self.server, port=self.port,
                                        user=self.username,
                                        password=self.password)
        return connection.search(self.base, 'sub', value)