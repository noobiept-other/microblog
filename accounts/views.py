from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from accounts.forms import MyUserCreationForm, PrivateMessageForm, EditAccountForm
from accounts.models import PrivateMessage
from accounts.decorators import must_be_staff, must_be_moderator
from microblog import utilities


def new_account( request ):
    """
        Create a new user account.
    """
    if request.method == 'POST':

        form = MyUserCreationForm( request.POST )

        if form.is_valid():

            form.save()
            utilities.add_message( request, "User '{}' created!".format(  form.cleaned_data[ 'username' ] ) )

            return HttpResponseRedirect( reverse( 'accounts:login' ) )

    else:
        form = MyUserCreationForm()

    context = {
        'form': form
    }

    return render( request, 'accounts/new_account.html', context )


def login( request ):
    """
        Login an account.
    """
    context = {}
    utilities.get_messages( request, context )

    return django_login( request, 'accounts/login.html', extra_context= context )


def user_page( request, username, what= None ):
    """
        The user page has information about an user account.
        Also where you can change some settings (like the password).
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    context = {}

    if what == 'images':
        allElements = user.get_messages_with_images()
        context[ 'imagesSelected' ] = True

    elif what == 'followers':
        allElements = user.get_followers()
        context[ 'followersSelected' ] = True

    elif what == 'following':
        allElements = user.get_following()
        context[ 'followingSelected' ] = True

    else:   # 'messages'
        allElements = user.posts.all().order_by( '-date_created' )
        context[ 'postSelected' ] = True


    paginator = Paginator( allElements, 5 )
    page = request.GET.get( 'page' )

    try:
        elements = paginator.page( page )

    except PageNotAnInteger:
        elements = paginator.page( 1 )  # first page

    except EmptyPage:
        elements = paginator.page( paginator.num_pages )  # last page


    context.update({
        'pageUser': user,
        'unreadMessages': user.how_many_unread_messages(),
        'elements': elements,
    })

    utilities.get_messages( request, context )

    return render( request, 'accounts/user_page.html', context )


@login_required
def message_send( request, username ):
    """
        Send a private message to another user.
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( 'Invalid username.' )


    if request.method == 'POST':
        form = PrivateMessageForm( request.POST )

        if form.is_valid():

            title = form.cleaned_data[ 'title' ]
            content = form.cleaned_data[ 'content' ]
            PrivateMessage.objects.create( receiver= user, sender= request.user, title= title, content= content )

            utilities.add_message( request, 'Message sent to {}!'.format( user ) )

            return HttpResponseRedirect( user.get_url() )

    else:
        form = PrivateMessageForm()

    context = {
        'form': form,
        'receiver': user
    }

    return render( request, 'accounts/send_message.html', context )


@login_required
def message_all( request ):

    messages = request.user.privatemessage_set.all()

    context = {
        'messages': messages
    }

    utilities.get_messages( request, context )

    return render( request, 'accounts/check_messages.html', context )


@login_required
def message_open( request, messageId ):
    """
        Open a particular private message.
    """
    try:
        message = request.user.privatemessage_set.get( id= messageId )

    except PrivateMessage.DoesNotExist:
        raise Http404( "Couldn't find that message." )

    if not message.has_been_read:
        message.has_been_read = True
        message.save( update_fields= [ 'has_been_read' ] )

    context = {
        'private_message': message
    }

    return render( request, 'accounts/open_message.html', context )


@login_required
def message_remove_confirm( request, messageId ):
    """
        Confirm the message removal.
    """
    try:
        message = request.user.privatemessage_set.get( id= messageId )

    except PrivateMessage.DoesNotExist:
        raise Http404( "Didn't find the message." )

    else:
        context = {
            'private_message': message
        }

        return render( request, 'accounts/remove_message.html', context )


@login_required
def message_remove( request, messageId ):
    """
        Remove a private message.
    """
    try:
        message = request.user.privatemessage_set.get( id= messageId )

    except PrivateMessage.DoesNotExist:
        raise Http404( "Message doesn't exist." )

    message.delete()
    utilities.add_message( request, 'Message removed!' )

    return HttpResponseRedirect( reverse( 'accounts:message_all' ) )


@must_be_staff
def set_moderator_confirm( request, username ):
    """
        Confirm giving/removing moderator rights to/from an user.
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    else:
        context = {
            'user_to_change': user
        }
        return render( request, 'accounts/change_moderator.html', context )


@must_be_staff
def set_moderator( request, username ):
    """
        Give/remove moderator rights from an account.
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    user.is_moderator = not user.is_moderator
    user.save( update_fields= [ 'is_moderator' ] )

    if user.is_moderator:
        message = "'{}' is now a moderator.".format( user )

    else:
        message = "'{}' is not a moderator anymore.".format( user )

    utilities.add_message( request, message )

    return HttpResponseRedirect( user.get_url() )


def password_changed( request ):
    """
        Inform that the password has been changed, and redirect to home.
    """
    utilities.add_message( request, 'Password changed!' )

    return HttpResponseRedirect( reverse( 'home' ) )


@login_required
def edit_account( request ):

    if request.method == 'POST':

        form = EditAccountForm( request.POST, request.FILES )

        if form.is_valid():

            name = form.cleaned_data[ 'name' ]
            info = form.cleaned_data[ 'info' ]
            image = request.FILES.get( 'image' )

            request.user.name = name
            request.user.info = info

            if image:
                request.user.image = image

            request.user.save( update_fields= [ 'name', 'info', 'image' ] )

            return HttpResponseRedirect( request.user.get_url() )

    else:
        form = EditAccountForm( initial= { 'name': request.user.name, 'info': request.user.info } )

    context = {
        'form': form
    }

    return render( request, 'accounts/edit_account.html', context )


@must_be_staff
def remove_user_confirm( request, username ):
    """
        Confirm an user removal.
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    context = {
        'user_to_remove': user
    }

    return render( request, 'accounts/remove_user.html', context )


@must_be_staff
def remove_user( request, username ):
    """
        Remove an user account (also removes everything associated with it).
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    else:
        utilities.add_message( request, "'{}' user removed!".format( user ) )
        user.delete()

        return HttpResponseRedirect( reverse( 'home' ) )


@must_be_moderator
def disable_user_confirm( request, username ):
    """
        Confirm the enabling/disabling of an user account.
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    else:
        context = {
            'user_to_disable': user
        }

        return render( request, 'accounts/disable_user.html', context )


@must_be_moderator
def disable_user( request, username ):
    """
        Enable/disable an user account.
        If the account is disabled, the user won't be able to login.
    """
    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    else:
        value = not user.is_active

            # only other staff users can enable/disable staff users
        if user.is_staff:
            if request.user.is_staff:
                user.is_active = value
                user.save( update_fields= [ 'is_active' ] )

            else:
                return HttpResponseForbidden( "Can't disable a staff member." )

        else:
            user.is_active = value
            user.save( update_fields= [ 'is_active' ] )


        if value:
            message = "'{}' account is now active.".format( user )

        else:
            message = "'{}' account is now disabled.".format( user )

        utilities.add_message( request, message )

        return HttpResponseRedirect( user.get_url() )
