from django import template
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe

import re

register = template.Library()

@register.filter
def category_links( text ):
    """
        Receives a text, search for the categories (in the form: #categoryName), and replaces it with a <a> tag with the appropriate link
    :param text:
    :return:
    """

    def addLink( match ):

        category = match.group( 1 )
        url = reverse( 'show_category', args= [ category ] )

        return '<a href="{}">#{}</a>'.format( url, category )

    result = re.sub( r'#(\w+)', addLink, text )

    return mark_safe( result )


@register.filter
def is_following( user, userToCheck ):

    return user.is_following( userToCheck )
