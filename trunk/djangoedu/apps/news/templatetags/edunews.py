from django import template

from djangoedu.apps.news.models import Story, ImportantDate

register = template.Library()


class StoryNode(template.Node):
    def __init__(self, slug, number, var_name):
        self.slug = slug
        self.number = number
        self.var_name = var_name

    def render(self, context):
        stories = Story.objects.published().filter(sections__slug=self.slug
            ).order_by('-publish_date')[:self.number]
        print 'stories:', stories
        if self.number == 1:
            if stories:
                context[self.var_name] = stories[0]
            else:
                context[self.var_name] = None
        else:
            context[self.var_name] = stories
        print context
        return ''

def story(parser, token):
    """
    Returns the latest news story or stories.
    
    Inputs:
    
    * ``slug`` - Slug of the section to grab news stories for.
    * ``number`` - The number of news stories to grab.
    * ``variable`` - The name of the template variable to save the stories to.
    
    Syntax::
    
        {% story <slug> <number> as <variable> %}
        
    Example::
    
        {% story "grad" 1 as story %}
    """
    tokens = token.split_contents()
    usage = ("Tag should be in the form of:"
             " {% story <slug> <number> as <variable> %}")
    if len(tokens) != 5 or tokens[3] != 'as':
        raise template.TemplateSyntaxError(usage)
    try:
        number = int(tokens[2])
    except ValueError:
        raise template.TemplateSyntaxError("number must be an integer.  " + usage)
    slug = tokens[1]
    if (slug.startswith('"') and slug.endswith('"')
            or (slug.startswith("'") and slug.endswith("'"))):
        slug = slug[1:-1]
    return StoryNode(slug, number, tokens[4])
register.tag('story', story)


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
