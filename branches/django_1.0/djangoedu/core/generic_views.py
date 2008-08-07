"""
=============
Generic Views
=============

Class based helper views.
"""

class GenericManyToMany(object):
    """Generic view to edit many to many relations with extra fields."""
    
    left_table = None
    right_table = None
    allow_multiple = True
    