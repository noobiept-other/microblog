from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

import uuid


class Category( models.Model ):

    name = models.SlugField( max_length= 100 )

    def __str__(self):
        return self.name

    def get_url(self):
        return reverse( 'show_category', args= [ self.name ] )


class Thread( models.Model ):

    user = models.ForeignKey( settings.AUTH_USER_MODEL )
    text = models.TextField( max_length= 200 )
    image = models.FileField( upload_to= 'images/%Y_%m_%d', blank= True )
    date_created = models.DateTimeField( default= timezone.now )
    categories = models.ManyToManyField( Category )
    identifier = models.CharField( max_length= 40, unique= True, default= uuid.uuid4 )

    def __str__(self):
        return self.text

    def get_url(self):
        return reverse( 'show_message', args= [ self.identifier ] )

    def get_thread_identifier(self):
        return self.identifier

    class Meta:
        ordering = [ '-date_created' ]


class Post( models.Model ):

    user = models.ForeignKey( settings.AUTH_USER_MODEL )
    text = models.TextField( max_length= 200 )
    image = models.FileField( upload_to= 'images/%Y_%m_%d', blank= True )
    date_created = models.DateTimeField( default= timezone.now )
    categories = models.ManyToManyField( Category )
    thread = models.ForeignKey( Thread )
    position = models.IntegerField()
    identifier = models.CharField( max_length= 40, unique= True, default= uuid.uuid4 )

    def __str__(self):
        return self.text

    def get_url(self):
        return '{}#post{}'.format( reverse( 'show_message', args= [ self.thread.identifier ] ), self.position )

    def get_thread_identifier(self):
        return self.thread.identifier

    class Meta:
        ordering = [ '-date_created' ]


