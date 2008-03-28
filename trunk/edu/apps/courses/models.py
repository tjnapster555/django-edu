from django.db import models
from django.conf import settings

# grab defaults from settings file
try:
    COURSE_LEVELS = settings.COURSE_LEVELS
except:
    COURSE_LEVELS = (
            ('L', _('Lower Division')),
            ('U', _('Upper Division')),
            ('G', _('Graduate')),
        )
    
class Course(models.Model):
    """*Courses*

    Each unique course# and course title.
    This model is used to make it easier to search and enter couses
    for the many different Models that use them.
    """

    department = models.ForeignKey(Department, verbose_name=_("Department"))
    level = models.CharField(_("Level"), max_length=4, choices=COURSE_LEVELS)
    credits = models.PositiveSmallIntegerField(_("Number of Credits"))
    pre_number = models.CharField(_("Pre Course Number"), max_length=25, blank=True)
    number = models.PositiveSmallIntegerField(_("Course Number"), db_index=True)
    post_number = models.CharField(_("Extra Course Number"), max_length=25,
        blank=True)
    title = models.CharField(_("Course Title"), max_length=255)

    def __unicode__(self):
        return u"%s %s%i%i%s" % (self.department.abbr, self.credits, 
            self.pre_number, self.number, self.post_number)

    def short_title(self):
        """Returns a truncated title useful for table displays and menus."""
        title =  u"%s: %s" % (unicode(self), self.title)
        return title[:22]
    
    class Meta:
        ordering = ('number', 'pre_number', 'post_number', 'title')
        unique_together = ('department', 'pre_number', 'number', 'post_number', 'title')

    class Admin:
        list_display = ('__unicode__', 'level', 'last_update')
        list_filter = ['level']
        list_per_page = 400

class CourseOffering(models.Model):
    """Course Offering.
    
    Time/Professor/Meets with information
    """
    