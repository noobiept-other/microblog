from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model


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

    def has_moderator_rights(self):
        if self.is_staff or self.is_moderator:
            return True

        return False

    def how_many_unread_messages(self):
        return self.privatemessage_set.filter( has_been_read= False ).count()

    def get_followers(self):
        userModel = get_user_model()

        return userModel.objects.filter( following__username= self.username )

    def get_following(self):
        return self.following.all()

    def get_message_count(self):
        return self.posts.count()

    def get_images_count(self):
        count = 0

        for post in self.posts.all():
            if post.image:
                count += 1

        return count

    def get_messages_with_images(self):

        messages = []

        for post in self.posts.all():
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

    def __str__(self):
        return self.username


class PrivateMessage( models.Model ):

    receiver = models.ForeignKey( settings.AUTH_USER_MODEL )
    sender = models.ForeignKey( settings.AUTH_USER_MODEL, related_name= 'sender' )
    title = models.TextField( max_length= 100 )
    content = models.TextField( max_length= 500 )
    date_created = models.DateTimeField( help_text= 'Date Created', default= timezone.now )
    has_been_read = models.BooleanField( default= False )

    def __str__(self):
        return self.title

    def get_url(self):
        return reverse( 'accounts:message_open', args= [ self.id ] )

    def get_date_created_number(self):
        """
            Time since the date it was created until the current time.
            Returns a float, useful for comparisons/sorting/etc.
        """
        diff = timezone.now() - self.date_created

        return diff.total_seconds()

    class Meta:
        ordering = [ '-date_created' ]