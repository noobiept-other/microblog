from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

import re

from microblog import utilities
from microblog.forms import PostForm
from microblog.models import Thread, Post, Category


@login_required
def home( request ):

    context = {
        'messages': request.user.get_last_following_messages()
    }

    utilities.get_message( request, context )

    return render( request, 'home.html', context )


@login_required
def post_message( request, threadIdentifier= None ):

    if request.method == 'POST':

        form = PostForm( request.POST, request.FILES )

        if form.is_valid():

            text = form.cleaned_data[ 'text' ]
            categories = re.findall( r'#(\w+)', text )
            image = request.FILES.get( 'image' )

            if threadIdentifier:
                try:
                    thread = Thread.objects.get( identifier= threadIdentifier )

                except Thread.DoesNotExist:
                    raise Http404( "Invalid thread identifier." )

                message = Post.objects.create( user= request.user, text= text, image= image, thread= thread, position= thread.post_set.count() + 2 )   # the +2 is because the position starts at 1 rather than 0, and the thread itself is considered the position 1 (so posts start at 2+)

            else:
                message = Thread.objects.create( user= request.user, text= text, image= image )

            for category in categories:

                try:
                    categoryElement = Category.objects.get( name= category )

                except Category.DoesNotExist:
                    categoryElement = Category.objects.create( name= category )

                message.categories.add( categoryElement )

            return HttpResponseRedirect( message.get_url() )

    else:
        form = PostForm()

    context = {
        'form': form,
        'threadIdentifier': threadIdentifier
    }

    return render( request, 'post.html', context )


@login_required
def set_follow( request, username ):

    userModel = get_user_model()

    if username == request.user.username:
        raise Http404( "Can't follow yourself." )

    try:
        userToFollow = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )


        # figure out if we're following or un-following
    try:
        request.user.following.get( username= username )

    except userModel.DoesNotExist:
        request.user.following.add( userToFollow )

        utilities.set_message( request, '{} followed'.format( userToFollow ) )

    else:
        request.user.following.remove( userToFollow )

        utilities.set_message( request, '{} un-followed'.format( userToFollow ) )

    return HttpResponseRedirect( reverse( 'home' ) )


@login_required
def show_category( request, categoryName ):

    try:
        category = Category.objects.get( name= categoryName )

    except Category.DoesNotExist:
        raise Http404( "Category doesn't exist." )

    messages = []

    messages.extend( category.thread_set.all() )
    messages.extend( category.post_set.all() )

    utilities.sort_by_date( messages )

    context = {
        'categoryName': categoryName,
        'messages': messages
    }

    return render( request, 'category.html', context )


@login_required
def show_people( request ):

    userModel = get_user_model()

    following = []

        # don't consider the people you're already following
    for people in request.user.following.all():
        following.append( people.username )

        # and yourself as well
    following.append( request.user.username )

    context = {
        'users': userModel.objects.exclude( username__in= following )
    }

    return render( request, 'people.html', context )

@login_required
def show_categories( request ):

    categories = Category.objects.all()

    context = {
        'categories': categories
    }

    return render( request, 'categories.html', context )


def show_message( request, identifier ):

    try:
        thread = Thread.objects.get( identifier= identifier )

    except Thread.DoesNotExist:
        raise Http404( "Invalid identifier." )

    messages = [ thread ]
    messages.extend( thread.post_set.all() )

    utilities.sort_by_date( messages, False )

    context = {
        'messages': messages
    }

    return render( request, 'show_message.html', context )


def search( request ):

    if request.method != 'POST':
        return HttpResponseForbidden( 'Post request only' )

    searchText = request.POST[ 'SearchText' ]

    if not searchText or len( searchText ) < 3:
        utilities.set_message( request, 'Write a search text with 3 or more 3 characters.' )
        return HttpResponseRedirect( reverse( 'home' ) )

    userModel = get_user_model()

    people = userModel.objects.filter( username__icontains= searchText )
    categories = Category.objects.filter( name__icontains= searchText )
    messages = []

    messages.extend( Thread.objects.filter( text__icontains= searchText ) )
    messages.extend( Post.objects.filter( text__icontains= searchText ) )

    context = {
        'search': searchText,
        'people': people,
        'categories': categories,
        'messages': messages
    }

    return render( request, 'search.html', context )