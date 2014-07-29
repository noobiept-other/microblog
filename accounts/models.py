from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

from microblog import utilities

class Account( AbstractUser ):

    is_moderator = models.BooleanField( default= False )
    following = models.ManyToManyField( settings.AUTH_USER_MODEL, symmetrical= False )
    name = models.CharField( max_length= 30 )
    info = models.CharField( max_length= 200, default= '', blank= True )
    image = models.FileField( upload_to= 'accounts/%Y_%m_%d', blank= True )

    def save(self, *args, **kwargs):

            # first time saving the account, init. the name with the same string as in the username (the name can then be changed later on)
        if self.pk is None:
            self.name = self.username

        super( Account, self ).save( *args, **kwargs )

    def get_url(self):
        return reverse( 'accounts:user_page', args= [ self.username ] )

    def get_followers(self):

        userModel = get_user_model()

        return userModel.objects.filter( following__username= self.username )

    def get_following(self):
        return self.following.all()

    def get_message_count(self):
        return self.post_set.count() + self.thread_set.count()

    def get_images_count(self):
        count = 0

        for thread in self.thread_set.all():
            if thread.image:
                count += 1

        for post in self.post_set.all():
            if post.image:
                count += 1

        return count

    def get_messages_with_images(self):

        messages = []

        for thread in self.thread_set.all():
            if thread.image:
                messages.append( thread )

        for post in self.post_set.all():
            if post.image:
                messages.append( post )

        return messages


    def is_following(self, username):

        userModel = get_user_model()

        try:
            self.following.get( username= username )

        except userModel.DoesNotExist:
            return False

        else:
            return True


    def get_last_messages(self):
        """
            Returns the last messages (thread/post) by the user
        """

        messages = []
        messages.extend( self.thread_set.all()[ :5 ] )
        messages.extend( self.post_set.all()[ :5 ] )

        utilities.sort_by_date( messages )

        return messages[ :5 ]


    def get_last_following_messages(self):
        """
            Returns the last messages (thread/post) written by users we're following
        """

        followingUsers = self.following.all()
        messages = []

            # get last 5 posts of each
        for following in followingUsers:
            messages.extend( following.thread_set.all()[ :5 ] )
            messages.extend( following.post_set.all()[ :5 ] )

        utilities.sort_by_date( messages )

        return messages[ :5 ]




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