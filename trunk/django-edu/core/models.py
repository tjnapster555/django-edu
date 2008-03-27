from django.db import models
from django.conf import settings

try:
    import mptt
except ImportError:
    raise ImproperlyConfigured, "You're missing django-mptt, go get it here: http://code.google.com/p/django-mptt/"

# grab defaults from settings file
try:
    SEMESTER_LIST = settings.SEMESTER_LIST
except:
    SEMESTER_LIST = (
            ('2', _('Spring')),
            ('6', _('Summer')),
            ('9', _("Fall")),
        )

class SemesterManager(models.Manager):
    """Custom Semester Manager
    
    Extra query provided:
    
    * ``current_semester([date])``: Returns the current semester or the next
      semester if date is in between semesters. Raises DoesNotExist
      if no matching semester is found. Default date is todays date.

    """
    
    def current_semester(self, date=None):
        """Returns the current semester.
        
        Options:
        
        * ``date``: (Optional) Defaults to todays date, if passed returns
          the semester for that contains the date.
        
        Example::
    
           >>> import datetime
           >>> now = datetime.datetime.now().date()
           >>> tomorrow = now + datetime.timedelta(days=1)
           >>> yesterday = now - datetime.timedelta(days=1)
           >>> next_week = now + datetime.timedelta(weeks=1)
       
           # No semesters should raise DoesNotExit
           >>> Semester.objects.current_semester()
           Traceback (most recent call last):
           ...
           Exception: DoesNotExist
           
           # Create a current semester
           >>> Semester.objects.create(year=now.year(),semester='2',sdate=now,edate=tomorrow)
           >>> Semester.objects.current_semester()
           <Semester: ...>
           
           # Optionally specify the date to check
           >>> Semester.objects.current_semester(date=yesterday)
           <Semester: ...>
           >>> Semester.objects.current_semester(date=next_week)
           Traceback (most recent call last):
           ...
           Exception: DoesNotExist
        """
        if not date:
            import datetime
            date = datetime.datetime.now().date()
            
        try:
            return self.get(sdate__lte=date, edate__gte=date)
        except self.model.DoesNotExist:
            objs = self.get_query_set().filter(sdate__gte=date).order_by('sdate')
            if objs:
                # first one should be the next semester
                return objs[0]
        raise self.model.DoesNotExist

class Semester(models.Model):
    """*Semesters*

    Holds the semesters information. Storing the primary key in CCYYS format.
    See: http://www.unece.org/trade/untdid/d03a/tred/tred2379.htm

    This model allows us to sort and print the CCYYS better then with template tags.
    """
    ccyys = models.PositiveIntegerField(primary_key=True, editable=False)
    year = models.PositiveIntegerField(_("Year"))
    semester = models.PositiveIntegerField(_("Semester"), choices=SEMESTER_LIST)
    sdate = models.DateField(_("Start of Semester"))
    edate = models.DateField(_("End of Semester"))

    objects = SemesterManager()
    
    def __unicode__(self):
        return u"%s %s" % (unicode(self.get_semester_display()), self.year)

    def save(self):
        self.ccyys = u"%s%s" % (self.year, self.semester)
        super(Semester, self).save()

    def yys(self):
        """Returns just the last three digits of the ccyys."""
        return self.ccyys[2:]
        
    class Meta:
        ordering = ['-ccyys']
        unique_together = ['year', 'semester']

    class Admin:
        list_display = ('year', 'semester', 'sdate', 'edate')

class Organization(models.Model):
    """*Organization*
    
    A Heirarchy of Organizations internal and external. When adding a 
    organization the organization is inserted alphabetically. The tree 
    structure if the data is maintained by the django-mptt application. 
    For more information please visit the django-mptt project page:
    http://code.google.com/p/django-mptt/
    
    By using mptt we can store an large number of sub groups and easily
    query only the part we are interested in. 
    
    Consider the example::
    
       Internal Organizations             External Organization
       ----------------------------       ---------------------------
       University of State                IEEE
       |                                  |
       +---College of Liberal Arts        +---IEEE Chapter at myU
       |   |
       |   +---Dept. of English
       |   |
       |   +---Dept. of German
       |
       +---College of Science
           |
           +---Dept. of Math
    
    A query that returns the "College of Liberal Arts" would return only 
    the subtree::
    
       College of Liberal Arts
       |
       +---Dept. of English
       |
       +---Dept. of German
    
    Resulting in less queries to the database server.
    """
    parent = models.ForeignKey('self', null=True, editable=False, 
        related_name='children')
    name = models.CharField(_("Department Name"), max_length=255)
    abbr = models.CharField(_("Abbreviation"), max_length=25, blank=True)
    website = models.URLField(_("Web Site"), verify_exists=False, blank=True)
    logo = models.ImageField(_("Logo"), blank=True, null=True)
    contact = models.ForeignKey(User, verbose_name=_("Contact Person"), null=True)
    # extra 'hidden' MPTT fields
    lft = models.PositiveIntegerField(db_index=True, editable=False)
    rght = models.PositiveIntegerField(db_index=True, editable=False)
    tree_id = models.PositiveIntegerField(db_index=True, editable=False)
    level = models.PositiveIntegerField(db_index=True, editable=False)
    
    def __unicode__(self):
        return self.abbr
    
    class Admin:
        list_display = ('abbr', 'name')

mptt.register(Organization, order_insertion_by='name')
        
class EduPerson(models.Model):
    """*Edu Person*
    
    This model uses some standard eduPerson attributes you can find more 
    information here: http://middleware.internet2.edu/dir/schema/
    
    """
    first_name = models.CharField(_("First Name"), max_length=255)
    last_name = models.CharField(_("Last Name"), max_length=255)
    nick_name = models.CharField(_("Nick Name"), max_length=255, blank=True)