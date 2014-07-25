from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse

class Post( models.Model ):

    user = models.ForeignKey( settings.AUTH_USER_MODEL )
    text = models.TextField( max_length= 200 )
    date_created = models.DateTimeField( default= lambda: timezone.localtime( timezone.now() ) )

    def __unicode__(self):
        return self.text

    def get_url(self):
        pass    #HERE


    class Meta:
        ordering = [ '-date_created' ]