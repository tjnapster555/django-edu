"""
=============
Course Models
=============

These models try to map as closely as possible to the `LDAP eduCourse data 
models`_. 

.. _LDAP eduCourse data models: http://middleware.internet2.edu/courseid/docs/internet2-mace-dir-courseID-eduCourse-200507.html

"""

from django.utils.translation import ugettext as _
from django.db import models
from django.conf import settings
from django.core import validators

from edu.core.models import eduPerson

# grab defaults from settings file
try:
    COURSE_TRUNCATE_LENGTH = settings.COURSE_TRUNCATE_LENGTH
except:
    COURSE_TRUNCATE_LENGTH = 22

# set the default TimeFrame model (Semesters, Quarters etc.)
try:
    TimeFrame = __import__(settings.TIME_FRAME_MODEL)
except:
    from edu.core.models import Semester as TimeFrame

try:
    Department = __import__(settings.DEPARTMENT_MODEL)
except:
    from edu.core.models import Organization as Department
    
class Course(models.Model):
    """*Courses*

    Each unique course# and course title.
    This model is used to make it easier to search and enter couses
    for the many different Models that use them.
    """
    cross_list = models.ManyToManyField('self', verbose_name=_("Cross Listed As"), 
        blank=True, null=True, related_name="cross_listings")
    parent = models.ForeignKey('self', verbose_name=_("Parent Course"),
        blank=True, null=True, related_name="children",
        help_text=_("Is this course part a of larger course, sometimes used for topics courses"))
    department = models.ForeignKey(Department, verbose_name=_("Department"))
    prefix = models.CharField(_("Prefix"), max_length=25, blank=True,
        help_text=_("Usually used to indicate summer sessions"))
    number = models.CharField(_("Course Number"), db_index=True, max_length=25)
    title = models.CharField(_("Course Title"), max_length=255)
    abstract = models.TextField(_("Abstract"), blank=True, 
        help_text=_("If this course has a parent then this abstract will be appended to the parents abstract."))
    prerequisite = models.TextField(_("Prerequisite"), blank=True,
        help_text=_("If this course has a parent then this prereq will be appended to the parents prereq."))

    def __unicode__(self):
        return u"%s %s: %s" % (unicode(self.department), self.number, self.title)

    def short_title(self):
        """Returns a truncated title useful for table displays and menus."""
        return unicode(self)[:COURSE_TRUNCATE_LENGTH]
    
    class Meta:
        ordering = ('department', 'number')

    class Admin:
        list_display = ('__unicode__', 'department')
        list_filter = ['department']
        list_per_page = 400

class CourseOffering(models.Model):
    """Course Offering.
    
    This is an instance of a course (Phys 101 offered during Spring 2008).
    """
    course = models.ForeignKey(Course, verbose_name=_("Course"))
    timeFrame = models.ForeignKey(TimeFrame, verbose_name=_("Time Frame"))
    cross_list = models.ManyToManyField('self', verbose_name=_("Cross Listed As"), 
        blank=True, null=True, related_name="cross_listings")
    
    def __unicode__(self):
        return u"%s %s" % (self.course, self.timeFrame)
    
    class Meta:
        unique_together = ('course', 'timeFrame')

class SectionType(models.Model):
    """Section Types
    
    Examples:
    
    * Lecture
    * Lab
    * Recitation
    * Discussion
    """
    name = models.CharField(max_length=255)
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass

class OfferingSection(models.Model):
    """Offering Section, an instance of an course offering."""
    parent = models.ForeignKey('self', verbose_name=_("Parent Section"), 
        blank=True, null=True, related_name='subsection')
    offering = models.ForeignKey(CourseOffering, verbose_name=_("Course Offering"))
    unique_number = models.PositiveIntegerField(_("Unique Number"), 
        blank=True, null=True,
        validator_list=[validators.RequiredIfOtherFieldNotGiven('parent')])
    # TODO: update this to new model validation whenever it lands in trunk
    type = models.ForeignKey(SectionType, verbose_name=_("Type"))
    credits = models.PositiveSmallIntegerField(_("Credits"), blank=True, null=True)
    meeting_days = models.CharField(_("Meeting Days"), max_length=255, blank=True)
    meeting_time = models.CharField(_("Meeting Time"), max_length=255, blank=True)
    meeting_place = models.CharField(_("Meeting Place"), max_length=255, blank=True)
    
    def __unicode__(self):
        return unicode(self.offering)
    
    class Admin:
        pass

class RoleType(models.Model):
    """Membership Roles.
    
    Examples: (Learner, Instructor, Member, Grader, Teaching Assistant, etc.)
    """
    name = models.CharField(_("Name"), max_length=255)
    
    def __unicode__(self):
        return self.name
    
    class Admin:
        pass

class CourseMembership(models.Model):
    """Memberships
    
    A person connected to a Course Offering and/or an Offering Section.
    """
    offering = models.ForeignKey(CourseOffering, verbose_name=_("Course Offering"),
        blank=True, null=True)
    section = models.ForeignKey(OfferingSection, verbose_name=_("Offering Section"),
        blank=True, null=True)
    person = models.ForeignKey(eduPerson, verbose_name=_("EDU Person"))
    roleType = models.ForeignKey(RoleType, verbose_name=_("Role"))
    subRole = models.ForeignKey(RoleType, verbose_name=_("Sub Role"), 
        related_name="subrole", blank=True, null=True)
    status = models.BooleanField(_("Status"), default=True)
    date = models.DateTimeField(_("Status Date"))
    
    def save(self):
        """Set the date to current time on change."""
        import datetime
        self.date = datetime.datetime.now()
        super(Membership, self).save()
        
    def __unicode__(self):
        if not self.section:
            return u"%s@%s" % (unicode(self.roleType), unicode(self.offering))
        return u"%s@%s" % (unicode(self.roleType), unicode(self.section))