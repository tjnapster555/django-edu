from django import template

from djangoedu.apps.news.models import Story, ImportantDate, Announcement

register = template.Library()


class LatestPublicationNode(template.Node):
    """
    A template node that is meant to handle various publication models.
    
    Model must have ``publish_date`` field and a ``published`` method on its
    ``objects`` manager.
    """
    
    def __init__(self, model, slug, number, var_name):
        self.model = model
        self.slug = slug
        self.number = number
        self.var_name = var_name

    def render(self, context):
        objects = self.model.objects.published().filter(
            sections__slug=self.slug).order_by('-publish_date')
        if self.number:
            objects = objects[:self.number]
        if self.number == 1:
            if objects:
                context[self.var_name] = objects[0]
            else:
                context[self.var_name] = None
        else:
            context[self.var_name] = objects
        return ''

def story(parser, token):
    """
    Returns the latest news story or stories.
    
    Inputs:
    
    * ``slug`` - Slug of the section to grab news stories for.
    * ``number`` - The number of news stories to grab.  If zero, then grab all
                   stories for the section.
    * ``variable`` - The name of the template variable to save the stories to.
    
    Syntax::
    
        {% story <slug> <number> as <variable> %}
        
    Example::
    
        {% story "grad" 1 as story %}
    """
    return LatestPublicationNode(Story, *publication_parse_tokens(token))
register.tag('story', story)

def announcements(parser, token):
    """
    Returns the latest announcement or announcements.
    
    Inputs:
    
    * ``slug`` - Slug of the section to grab announcements for.
    * ``number`` - The number of announcements to grab.  If zero, then grab all
                   announcements for the section.
    * ``variable`` - The name of the template variable to save the
                     announcements to.
    
    Syntax::
    
        {% announcements <slug> <number> as <variable> %}
        
    Example::
    
        {% announcements "grad" 1 as story %}
    """
    return LatestPublicationNode(Announcement, *publication_parse_tokens(token))
register.tag('announcements', announcements)

def publication_parse_tokens(token):
    """
    Take a token from a publication templatetag parser function and return a
    3-tuple of (slug, number, variable).
    """
    tokens = token.split_contents()
    usage = ("Tag should be in the form of:"
             " {%% %s <slug> <number> as <variable> %%}" % tokens[0])
    if len(tokens) != 5 or tokens[3] != 'as':
        raise template.TemplateSyntaxError(usage)
    try:
        number = int(tokens[2])
    except ValueError:
        raise template.TemplateSyntaxError("number must be an integer.  " + usage)
    if number < 0:
        raise template.TemplateSyntaxError("number must be a positive integer.  " + usage)
    slug = tokens[1]
    if (slug.startswith('"') and slug.endswith('"')
            or (slug.startswith("'") and slug.endswith("'"))):
        slug = slug[1:-1]
    return (slug, number, tokens[4])


class DatesNode(template.Node):
    def __init__(self, slug, var_name):
        self.slug = slug
        self.var_name = var_name

    def render(self, context):
        dates = ImportantDate.objects.future().filter(sections__slug=self.slug
            ).order_by('date')
        context[self.var_name] = dates
        return ''

def dates(parser, token):
    """
    Returns the upcoming important dates for a section.
    
    Inputs:
    
    * ``slug`` - Slug of the section to grab news stories for.
    * ``variable`` - The name of the template variable to save the dates to.
    
    Syntax::
    
        {% dates <slug> as <variable> %}
        
    Example::
    
        {% dates "grad" as dates %}
    """
    tokens = token.split_contents()
    usage = ("Tag should be in the form of:"
             " {% dates <slug> as <variable> %}")
    if len(tokens) != 4 or tokens[2] != 'as':
        raise template.TemplateSyntaxError(usage)
    slug = tokens[1]
    if (slug.startswith('"') and slug.endswith('"')
            or (slug.startswith("'") and slug.endswith("'"))):
        slug = slug[1:-1]
    return DatesNode(slug, tokens[3])
register.tag('dates', dates)
