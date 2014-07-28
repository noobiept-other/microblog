from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

class Account( AbstractUser ):

    is_moderator = models.BooleanField( default= False )
    following = models.ManyToManyField( settings.AUTH_USER_MODEL, symmetrical= False )
    info = models.CharField( max_length= 200, default= '', blank= True )

    def get_url(self):
        return reverse( 'accounts:user_page', args= [ self.username ] )

    def get_followers(self):

        userModel = get_user_model()

        return userModel.objects.filter( following__username= self.username )

    def get_following(self):
        return self.following.all()

    def get_post_count(self):
        return self.post_set.count()

    def is_following(self, username):

        userModel = get_user_model()

        try:
            self.following.get( username= username )

        except userModel.DoesNotExist:
            return False

        else:
            return True

class PrivateMessage( models.Model ):

    receiver = models.ForeignKey( settings.AUTH_USER_MODEL )
    sender = models.ForeignKey( settings.AUTH_USER_MODEL, related_name= 'sender' )
    title = models.TextField( max_length= 100 )
    content = models.TextField( max_length= 500 )
    date_created = models.DateTimeField( help_text= 'Date Created', default= lambda: timezone.localtime( timezone.now() ) )

    def __unicode__(self):
        return self.title

    def get_url(self):
        return reverse( 'accounts:open_message', args= [ self.id ] )