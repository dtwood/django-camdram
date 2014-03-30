from django import template
from django.template.loader import get_template

register = template.Library()

class AdminPanelNode(template.Node):
    def __init__(self, item_name):
        self.item_name = item_name
        self.template = get_template('drama/admin_panel.html')
    def render(self, context):
        user = context['user']
        item = context[self.item_name]
        if user.has_perm('drama.change_' + item.__class__.__name__, item):
            context = {}
            context['type'] = item.__class__.__name__.lower()
            context['item'] = item
            if user.has_perm('drama.admin_' + item.__class__.__name__, item):
                context['admin'] = True
            return self.template.render(template.Context(context))
        else:
            return ""
        
@register.tag
def admin_panel(parser, token):
    try:
        tag_name, item_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    return AdminPanelNode(item_name)
