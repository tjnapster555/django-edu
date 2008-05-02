from django.db import models
from sitebuilder.models import Section

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
    content = models.TextField(help_text="Place html content here.")
    publish_date = models.DateTimeField("Publication date/time",
        help_text="Enter the date and time you want this story to appear.")
    active = models.BooleanField(default=True,
        help_text="Uncheck ")
    more = models.ForeignKey("ECEFlatPage", blank=True, null=True, raw_id_admin=True,
        help_text="Link to the full news story this will show as a 'more...' link at the bottom of the content.")
    last_update = models.DateTimeField(auto_now=True)
    
    objects = ActiveManager()
        
    def __unicode__(self):
        return smart_unicode(self.title)
    
    class Meta:
        verbose_name_plural = "news stories"
        get_latest_by = "pubish_date"
      
    class Admin:
        list_display = ('title', 'publish_date', 'active')
        list_filter = ('publish_date', 'active')
        fields = (
            ("Title", {'fields': (('title', 'display_title'), 'slug',
                                  'publish_date')}),
            ("Body", {'fields': ('content', ('story_type', 'active'), 'more'),
                      'classes': 'extraLarge'}),
        )
        search_fields = ('title', 'content')
        save_on_top = True
        list_per_page = 15
        ordering = ('-publish_date',)
        
    def get_absolute_url(self):
        return reverse('news-display',
            args=[self.publish_date.year, self.publish_date.month,
                  self.publish_date.day, self.slug])


class Announcement(models.Model):
    """
    Announcements are brief stories for drawing attention to special events,
    or providing information.These quick stories display on the ECE Home Page in the scrolling 
    news window below the Main Cover Story. The Home page will display all
    the active '*News Flashes*'. The '*More link*' will be used as link 
    attached the the '*News Flash Title*' and the '*News Image*'.
    
    All the active '*News Flashes*' will also be displayed on the plamsa flash
    screen. '*News Flashes*' can manually set to inactive on the edit page or
    they can be set to expire at a certain date/time. The plasma screen will 
    automatically read the XML file produced by this Model. You can view that 
    xml file here: 
    http://www.ece.utexas.edu/plasma/news.xml
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(prepopulate_from=('title',)) 
    content = models.TextField()
    image = models.CharField(max_length=255,
        help_text="Please enter only the image name, ie. image.jpg")
    more_link = models.URLField(blank=True, null=True)
    pub_date = models.DateTimeField("Publish Date",
        help_text="Enter the date and time you want this news item to appear.")
    expire_date = models.DateTimeField(blank=True, null=True,
        help_text="""Enter the date and time you would like this news item to stop
            appearing.  Leaving this field blank will show the story
            indefinitely, as long as it is active.""")
    active = models.BooleanField(default=True)
    
    objects = ActiveManager()  
      
    def __unicode__(self):
        return smart_unicode(self.title)

    def get_absolute_url(self):
        return reverse('news-display', args=[self.pub_date.year,
                                             self.pub_date.month,
                                             self.pub_date.day,
                                             self.slug])
    
    class Meta:
        verbose_name = "News Flash"
        verbose_name_plural = "News Flashes"
        ordering = ('-pub_date',)
        
    class Admin:
        list_display = ('title', 'image', 'pub_date', 'expire_date', 'active')
        list_filter = ('pub_date', 'active')
        search_fields = ('title', 'content')
        save_on_top = True
        fields = (
            ("News Content", {'fields': (('active', 'title', 'slug'), 'content', 'image', 'more_link')}),
            ("Dates/Times", {'fields': (('pub_date', 'expire_date'),)}),
        )
