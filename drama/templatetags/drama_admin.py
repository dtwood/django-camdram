import string
import itertools
import markdown as markdown_lib
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.template.loader import get_template
from guardian.shortcuts import get_users_with_perms, get_groups_with_perms, get_perms_for_model
from django.contrib.auth.models import Permission
from drama.models import Venue

register = template.Library()

class AdminPanelNode(template.Node):
    def __init__(self, item_name):
        self.item_name = item_name
        self.template = get_template('drama/admin_panel.html')
    def render(self, context):
        user = context['user']
        item = context[self.item_name]
        type = item.__class__.__name__.lower()
        if user.has_perm('drama.change_' + type, item):
            subcontext = {}
            subcontext['approved'] = item.approved
            subcontext['type'] = type
            subcontext['item'] = item
            admin_perm = 'change_' + type
            if user.has_perm(admin_perm, item):
                if type == 'show':
                    subcontext['admin'] = True
                    subcontext['users'] = get_users_with_perms(item, with_group_users=False)
                    subcontext['pending_users'] = item.pendingadmin_set.all()
                    groups = list(get_groups_with_perms(item))
                    if type == 'show':
                        groups = groups + [item.society.group]
                        for venue in Venue.objects.filter(performance__show=item).distinct():
                            groups = groups + [venue.group]
                    subcontext['groups'] = groups
                    
                elif type == 'venue' or type == 'society':
                    subcontext['admin'] = True
                    if item.group:
                        subcontext['users'] = item.group.user_set.all()
                        subcontext['pending_users'] = item.group.pendinggroupmember_set.all()
            if user.has_perm('drama.approve_' + type, item):
                subcontext['approve'] = True
            return self.template.render(template.Context(subcontext))
        else:
            return ""
        
@register.tag
def admin_panel(parser, token):
    try:
        tag_name, item_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    return AdminPanelNode(item_name)


class DefaultMenuNode(template.Node):
    def __init__(self):
        self.template = get_template('drama/default_menu.html')

    def render(self, context):
        user = context['user']
        subcontext = {
            'add_show':user.has_perm('drama.add_show'),
            'add_venue':user.has_perm('drama.add_venue'),
            'add_role':user.has_perm('drama.add_role'),
            'add_society':user.has_perm('drama.add_society'),
            }
        return self.template.render(template.Context(subcontext))
        
        
@register.tag
def default_menu(parser, token):
    return DefaultMenuNode()

class AdvertLinksNode(template.Node):
    def __init__(self, item_name):
        self.item_name = item_name
        self.template = get_template('drama/advert_links.html')

    def render(self, context):
        user = context['user']
        advert = context[self.item_name]
        if advert.can_edit(user):
            advert = context[self.item_name]
            subcontext = {
                'advert': advert
                }
            return self.template.render(template.Context(subcontext))
        return HttpResponse('')

@register.tag
def advert_links(parser, token):
    try:
        tag_name, item_name = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    return AdvertLinksNode(item_name)

_the_string = ''.join([string.ascii_uppercase,string.ascii_lowercase])
class AlphabetNode(template.Node):
    def render(self, context):
        if self not in context.render_context:
            context.render_context[self] = itertools.cycle(_the_string)
        alph_iter = context.render_context[self]
        return next(alph_iter)

@register.tag
def alphabet(parser, token):
    return AlphabetNode()
        

@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    extensions = []

    return mark_safe(markdown_lib.markdown(value,
                                       extensions,
                                       safe_mode='escape',
                                       enable_attributes=False))
