from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

import uuid


POST_MAX_LENGTH = 200


class Category( models.Model ):

    name = models.SlugField( max_length= 100 )

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse( 'show_category', args= [ self.name ] )


class Post( models.Model ):

    user = models.ForeignKey( settings.AUTH_USER_MODEL, related_name= 'posts' )
    text = models.TextField( max_length= POST_MAX_LENGTH )
    image = models.FileField( upload_to= 'images/%Y_%m_%d', blank= True )
    date_created = models.DateTimeField( default= timezone.now )
    categories = models.ManyToManyField( Category )
    reply_to = models.ForeignKey( 'self', related_name= 'replies', blank= True, null= True )
    identifier = models.UUIDField( unique= True, default= uuid.uuid4 )

    def __str__(self):
        return self.text

    def get_url(self):
        return reverse( 'show_message', args= [ self.identifier ] )

    class Meta:
        ordering = [ '-date_created' ]


