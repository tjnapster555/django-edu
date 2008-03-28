import ldap

from django.db import models
from django.conf import settings

class LdapObjectField(models.Field):
    """This is a special field the stores a DN which relates to a LDAP object.
    
    It allows you access to the ldap properties for that object. For example
    consider the following model::
    
       class Person(models.Model):
           name = models.CharField(max_length=255)
           ldap = LdapObjectField(lookup_param="dc=State, dc=Edu", 
                                  server="ldap.state.edu", port=389)
    
    Then if you added a person to this class you could do the following 
    lookup::
    
        >>> person = Person.objects.all()[0]
        >>> person.ldap.givenName 
        'FirstName'
    """
    __metaclass__ = models.SubfieldBase
    
    def __init(self, lookup_param, server=None, port=None):
        """Setup up ldap object field"""
        # if server/port are null use the defaults from settings.py
        self.server = server or settings.LDAP_SERVER
        self.port = port or settings.LDAP_SERVER_PORT
        return super(Field, self).__init__()
    
    def db_type(self):
        return 'varchar(255)'
    
    def to_python(self, value):
        """Lookup ldap object and return it."""
        #TODO: Make this field work(tm)    
        return None   