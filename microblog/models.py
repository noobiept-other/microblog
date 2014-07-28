from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

class Category( models.Model ):

    name = models.SlugField( max_length= 100 )

    def __unicode__(self):
        return self.name

    def get_url(self):
        return reverse( 'show_category', args= [ self.name ] )

class Post( models.Model ):

    user = models.ForeignKey( settings.AUTH_USER_MODEL )
    text = models.TextField( max_length= 200 )
    image = models.FileField( upload_to= 'images/%Y_%m_%d', blank= True )
    date_created = models.DateTimeField( default= lambda: timezone.localtime( timezone.now() ) )
    categories = models.ManyToManyField( Category )

    def __unicode__(self):
        return self.text

    def get_url(self):
        pass    #HERE


    class Meta:
        ordering = [ '-date_created' ]


