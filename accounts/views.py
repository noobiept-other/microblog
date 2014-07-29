from django.contrib.auth import get_user_model
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from accounts.forms import MyUserCreationForm, PrivateMessageForm, EditAccountForm
from accounts.models import PrivateMessage
from accounts.decorators import must_be_staff
import microblog.utilities as utilities


def new_account( request ):

    if request.method == 'POST':

        form = MyUserCreationForm( request.POST )

        if form.is_valid():

            form.save()
            return HttpResponseRedirect( reverse( 'accounts:login' ) )

    else:
        form = MyUserCreationForm()

    context = {
        'form': form
    }

    return render( request, 'accounts/new_account.html', context )


def user_page( request, username ):

    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    context = {
        'pageUser': user,
        'messages': user.get_last_messages(),
        'postSelected': True
    }

    utilities.get_message( request, context )

    return render( request, 'accounts/user_page.html', context )

@login_required
def show_followers( request ):

    followers = request.user.get_followers()

    context = {
        'pageUser': request.user,
        'users': followers,
        'followersSelected': True
    }

    return render( request, 'accounts/user_page.html', context )


@login_required
def show_following( request ):

    following = request.user.get_following()

    context = {
        'pageUser': request.user,
        'users': following,
        'followingSelected': True
    }

    return render( request, 'accounts/user_page.html', context )



@login_required
def send_private_message( request, username ):

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
            message = PrivateMessage( receiver= user, sender= request.user, title= title, content= content )
            message.save()


            return HttpResponseRedirect( user.get_url() )

    else:
        form = PrivateMessageForm()

    context = {
        'form': form,
        'username': username
    }

    return render( request, 'accounts/send_message.html', context )


@login_required
def check_message( request ):

    messages = request.user.privatemessage_set.all()

    context = {
        'messages': messages
    }

    utilities.get_message( request, context )

    return render( request, 'accounts/check_messages.html', context )


@login_required
def open_message( request, messageId ):

    try:
        message = PrivateMessage.objects.get( id= messageId )

    except PrivateMessage.DoesNotExist:
        raise Http404( "Message doesn't exist" )

    context = {
        'private_message': message
    }

    return render( request, 'accounts/open_message.html', context )

@login_required
def remove_message( request, messageId ):

    try:
        message = PrivateMessage.objects.get( id= messageId )

    except PrivateMessage.DoesNotExist:
        raise Http404( "Message doesn't exist." )

    if message.receiver != request.user:
        return HttpResponseForbidden( "Not your message." )

    message.delete()
    utilities.set_message( request, 'Message removed' )

    return HttpResponseRedirect( reverse( 'accounts:check_message' ) )


@must_be_staff
def set_moderator( request, username ):

    userModel = get_user_model()

    try:
        user = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )

    user.is_moderator = not user.is_moderator
    user.save()

    utilities.set_message( request, 'Set/clear the moderator rights.' )

    return HttpResponseRedirect( user.get_url() )


def password_changed( request ):

    utilities.set_message( request, 'Password changed' )

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

            request.user.save()

            return HttpResponseRedirect( request.user.get_url() )

    else:
        form = EditAccountForm( initial= { 'name': request.user.name, 'info': request.user.info } )

    context = {
        'form': form
    }

    return render( request, 'accounts/edit_account.html', context )