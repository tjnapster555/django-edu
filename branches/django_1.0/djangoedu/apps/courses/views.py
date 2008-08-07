"""
================================
Generic Views for Course Objects
================================

About
~~~~~

A common interface to deal with course related information. 

* Provides a way to list courses by (semester, professor, year, 
  department, etc...)
* Provide a common way to grant access and deny access to view/change info.
* Provide a common form to edit/update/add information.

Like New Forms Admin, it allows you to register a model 
and override any method defined in the API specs (url to come). 

"""

from courses.models import Course, CourseOffering, OfferingSection

def get_change_perm(model):
    return "%s.%s" % (model._meta.app_label, model._meta.get_change_perm())

def get_delete_perm(model):
    return "%s.%s" % (model._meta.app_label, model._meta.get_delete_perm())

class BidrectionalObjectView(object):
    """Handles CRUD views for objects which have 2 many to many relations.
    
    Basic example a Textbook is related to multiple Sections and a Section
    has multiple Textbooks. In the example some Textbooks are required and
    others are optional. In this case you need to have a third model which 
    relates Textbooks to Sections looking something like this::
    
        class TextbookSelection(models.Model):
             textbook = models.ForeignKey(Textbook)
             section = models.ForeignKey(Section)
             required = models.BooleanField()
              
    """
    allow_multiple = True
    group_by = ('semester', 'course', 'professor')
    edit_all_groups = True
    professor_allow_null = True
    course_model = Course
    offering_model = CourseOffering
    section_model = OfferingSection
   
    def __init__(self, model):
        """Set up the Edit View"""
        self.model = model
        
    def has_view_access(self, request):
        """Return True(default) or False if request user can view object."""
        return True
    
    def has_change_access(self):
        """Return True or False if request user can change object."""
        return request.user.has_perm(get_change_perm(self.model))
    
    def has_delete_access(self):
        """Return True or False if request user can delete object."""
        return request.user.has_perm(get_delete_perm(self.model))