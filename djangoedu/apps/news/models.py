from datetime import datetime

from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from sitebuilder.models import Section


class ActiveManager(models.Manager):
    """
    A manager that provides convenience methods for grabbing active/inactive
    objects.  This manager can be used with any Model with a BooleanField named
    "active".


    Can be used on any model with an active attribute.  Creates methods for
    returning only active objects or only inactive objects. If the model also
    has pub_date and/or expire_date you can also use the published or current
    shortcuts.
    """
    def active(self):
        return self.get_query_set().filter(active=True)

    def inactive(self):
        return self.get_query_set().filter(active=False)

    def published(self):
        """
        Returns active objects whose publication date has passed.  This method
        can only be used with Models that have a "publish_date" field.

        If the Model has an "expire_date" field, then only active objects whose
        publication date has passed and whose expiration date has not passed
        will be returned.
        """
        now = datetime.now()
        objects = self.active().filter(publish_date__lte=now)
        model_field_names = [field.name for field in self.model._meta.fields]
        if "expire_date" in model_field_names:
            objects = objects.filter(
                Q(expire_date__isnull=True) | Q(expire_date__gt=now))
        return objects


class Story(models.Model):
    """
    News stories can be marked for display on one or more sections of the
    website.  If you wish to test a story before it goes live, set the
    publication date to some date/time in the future, click "Save and
    Continue," then click the "View On Site" link at the top of the edit page.
    """
    sections = models.ManyToManyField(Section,
        help_text="Select the sections you would like this news story to be"
                  " displayed.")
    title = models.CharField("Story Title", max_length=255)
    slug = models.SlugField(prepopulate_from=('title',))
    display_title = models.BooleanField(default=True,
        help_text="Choose whether or not the title should be displayed.")
    image = models.ImageField(blank=True, null=True, upload_to='story_images',
        help_text="Image that will appear when the story is the featured story.")
    thumbnail = models.ImageField(blank=True, null=True,
        upload_to='story_thumbnails',
        help_text="A 83w X 63h image that gets displayed in the recent news box.")
    content = models.TextField(help_text="Place html content here.")
    publish_date = models.DateTimeField("Publication date/time",
        help_text="Enter the date and time you want this story to appear.")
    active = models.BooleanField(default=True)
    last_update = models.DateTimeField(auto_now=True)

    objects = ActiveManager()

    class Meta:
        verbose_name_plural = "stories"
        get_latest_by = "pubish_date"
        ordering = ('-publish_date',)

    class Admin:
        list_display = ('title', 'publish_date', 'active')
        list_filter = ('publish_date', 'active')
#        fields = (
#            ("Title", {'fields': (('title', 'display_title'), 'slug',
#                                  'publish_date')}),
#            ("Body", {'fields': ('content', 'active', 'more'),
#                      'classes': 'extraLarge'}),
#        )
        search_fields = ('title', 'content')
        save_on_top = True
        list_per_page = 15

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news-display',
            args=[self.publish_date.year, self.publish_date.month,
                  self.publish_date.day, self.slug])


class Announcement(models.Model):
    """
    Announcements are brief stories for drawing attention to special events,
    or providing information.  They are not archived.
    """
    sections = models.ManyToManyField(Section,
        help_text="Select the sections you would like this deadline to be"
                  " displayed.")
    title = models.CharField(max_length=255)
    text = models.TextField()
    image = models.ImageField(blank=True, null=True,
        upload_to='announcement_images')
    more_link = models.URLField(blank=True, null=True)
    publish_date = models.DateTimeField(
        help_text="Enter the date and time you want this announcement to appear.")
    expire_date = models.DateTimeField(blank=True, null=True,
        help_text="Enter the date and time you would like this announcement to"
                  " stop appearing.  Leaving this field blank will show the"
                  " story indefinitely, as long as it is active.")
    active = models.BooleanField(default=True)

    objects = ActiveManager()

    class Meta:
        ordering = ('-publish_date',)

    class Admin:
        list_display = ('title', 'image', 'publish_date', 'expire_date', 'active')
        list_filter = ('publish_date', 'active')
        search_fields = ('title', 'text')
        save_on_top = True

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news-display', args=[self.publish_date.year,
                                             self.publish_date.month,
                                             self.publish_date.day,
                                             self.slug])


class ImportantDateManager(models.Manager):
    """
    Manager for ImportantDate that provides a convenience method for grabbing
    dates for a specified number of months in the future.
    """

    def future(self, months=3):
        """
        Return a QuerySet of objects from today to months number of months into
        the future.  By default, months is 3.
        """
        today = datetime.today()
        return self.get_query_set().filter(
            # If object has no end_date, then date should be today or later.
            (Q(end_date__isnull=True) & Q(date__gte=today))
            # Or if object has an end_date, then we still want object to show
            # until end_date has passed.
             | Q(end_date__gte=today))


class ImportantDate(models.Model):
    """
    This model can be used as a way to publish important dates or deadlines.
    """
    sections = models.ManyToManyField(Section,
        help_text="Select the sections you would like this deadline to be"
                  " displayed.")
    text = models.CharField(max_length=100)
    date = models.DateField()
    end_date = models.DateField(blank=True, null=True,
        help_text="If the deadline covers a range of dates, then enter the"
                  " end date here.")
    link = models.URLField(blank=True, null=True)

    objects = ImportantDateManager()

    class Meta:
        get_latest_by = "date"

    class Admin:
        ordering = ('-date')
        list_display = ('text', 'date', 'end_date')
        list_filter = ('date', 'sections')
        search_fields = ('text',)

    def __unicode__(self):
        return u"%s - %s" % (unicode(self.date), unicode(self.text))
