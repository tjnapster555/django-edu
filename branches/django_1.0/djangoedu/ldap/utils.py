"""
Utilities for accessing LDAP databases.
"""

import ldap
import os.path

from django.utils.encoding import force_unicode

DEBUG = False
if DEBUG:
    # Set debugging level
    import sys
    ldap.set_option(ldap.OPT_DEBUG_LEVEL,255)
    ldapmodule_trace_level = 1
    ldapmodule_trace_file = sys.stderr

# RHEL4 seems to work out of the box without the need to set any TLS options.
# My gentoo system, OTOH, needs them.
if os.path.exists('/etc/gentoo-release'):
    # The ldap.pem was created using /etc/openldap/ssl/gencert.sh, part of the openldap package.
    # The /usr/share/ca-certificates directory is part of the ca-certificates package.
    ldap.set_option(ldap.OPT_X_TLS_CERTFILE, '/etc/openldap/ssl/ldap.pem')
    ldap.set_option(ldap.OPT_X_TLS_KEYFILE, '/etc/openldap/ssl/ldap.pem')
    ldap.set_option(ldap.OPT_X_TLS_CACERTDIR, '/usr/share/ca-certificates')

class LDAPConnection(object):
    
    def __init__(self, serverName, port=389, user="", password=""):
        """Set up the connection.
        
        user should be a DN.
        If no user and password is given, try to connect anonymously with a blank user DN and password.
        """
        
        url = 'ldap://%s:%s' % (serverName, str(port))
        self.connection = ldap.initialize(url)
        self.bind(user, password)
    
    def bind(self, dn, password):
        """Bind using the passed DN and password."""
        # It seems that python-ldap chokes when passed unicode objects with
        # non-ascii characters.  So if we have a unicode password, encode
        # it to utf-8.
        if isinstance(password, unicode):
            password = password.encode('utf-8')
        self.connection.simple_bind_s(dn, password)        
    
    def close(self):
        self.connection.unbind_s()
    
    def search(self, searchBaseDN, filter, scope=ldap.SCOPE_SUBTREE, returnAttributes=[]):
        results = self.connection.search_s(searchBaseDN, scope, filter, returnAttributes)
        return self.toItems(results)
    
    def toItems(self, results):
        """Return the LDAPResults as LDAPItems which is a dict storage container."""
        
        return [LDAPItem(item) for item in results]

class SecureLDAPConnection(LDAPConnection):
    """
    A class for setting up an LDAP connection over an encrypted channel and then sending queries
    over that connection.
    
    Example use:
    
        >>> ldaps = SecureLDAPConnection("ldap.state.edu", user="super", password="secret")
        >>> ldaps.close()
    """
    
    def __init__(self, serverName, port=636, user="", password=""):
        """
        Set up the connection.
        
        The default port for secure LDAP is 636.
        user should be a DN.
        If no user and password is given, try to connect anonymously with a blank user DN and password.
        """
        
        url = 'ldaps://%s:%s' % (serverName, str(port))
        self.connection = ldap.initialize(url)
        self.bind(user, password)

def lazy_unicode(s):
    """Attempt to return a unicode string fail silently."""
    try:
        return force_unicode(s)
    except:
        return s

class LDAPItem(dict):
    """
    Provides a storage container for LDAP objects, or anything with a DN and attributes.
    
    This is helpful for turning query results into a useful object.
    """
    
    def __init__(self, LDAPResult):
        """"""
        
        self.dn, self.attributes = LDAPResult
        for attribute, values in self.attributes.items():
            # force unicode attributes and values fail silently
            attr = lazy_unicode(attribute)
            value = [lazy_unicode(s) for s in values]
            # Make first value of each LDAP attribute accessible
            # through instance attribute of same name
            setattr(self, attr, value[0])
            # Make the entire list of values for each LDAP attribute 
            # accessible through a dictionary mapping
            self[attr] = value
    
    def __getattr__(self, attribute):
        # Return an empty string if the attribute doesn't exist
        return self.__dict__.get(attribute, '')

    def __getitem__(self, attribute):
        try:
            return dict.__getitem__(self, attribute)
        except KeyError:
            # Return an empty list if the attribute doesn't exist
            return []

    def __getstate__(self): 
        ''' Needed for cPickle in .copy() '''
        return self.__dict__.copy() 

    def __setstate__(self, dict): 
        ''' Needed for cPickle in .copy() '''
        self.__dict__.update(dict)
    
    def valueInAttribute(self, value, attribute):
        for item in self[attribute]:
            if value in item:
                return True
        return False
    
    def __unicode__(self):
        return unicode(self.dn)