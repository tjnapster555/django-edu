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
    number = models.PositiveSmallIntegerField(_("Course Number"), db_index=True)
    extra_number = models.CharField(_("Extra Course Number"), max_length=25)
    title = models.CharField(_("Course Title"), max_length=255)

    def __unicode__(self):
        return u"%s %i%i%s" % (self.department, self.credits, 
                               self.number, self.extra_number)

    def short_title(self):
        """Returns a truncated title useful for table displays and menus."""
        title =  u"%s: %s" % (unicode(self), self.title)
        return title[:22]
    
    class Meta:
        ordering = ('number', 'title')
        unique_together = ('department', 'number', 'extra_number', 'title')

    class Admin:
        list_display = ('__unicode__', 'level', 'last_update')
        search_fields = ('number', 'title')
        list_filter = ['level']
        list_per_page = 400  