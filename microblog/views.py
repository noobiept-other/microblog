from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

import re

import microblog.utilities as utilities
from microblog.forms import PostForm
from microblog.models import Post, Category

@login_required
def home( request ):

    followingUsers = request.user.following.all()

    posts = []

        # get last 5 posts of each
    for following in followingUsers:
        posts.extend( following.post_set.all()[ :5 ] )

    def sort_by_date(a, b):
        return int( (b.date_created - a.date_created).total_seconds() )

        # order by date
    posts.sort( sort_by_date )

    context = {
        'posts': posts[ :5 ]
    }

    utilities.get_message( request, context )

    return render( request, 'home.html', context )


@login_required
def post_message( request ):

    if request.method == 'POST':

        form = PostForm( request.POST, request.FILES )

        if form.is_valid():

            text = form.cleaned_data[ 'text' ]
            categories = re.findall( r'#(\w+)', text )
            image = request.FILES.get( 'image' )

            post = Post( user= request.user, text= text, image= image )
            post.save()

            for category in categories:

                try:
                    categoryElement = Category.objects.get( name= category )

                except Category.DoesNotExist:
                    categoryElement = Category( name= category )
                    categoryElement.save()

                post.categories.add( categoryElement )

            return HttpResponseRedirect( reverse( 'home' ) )

    else:
        form = PostForm()

    context = {
        'form': form
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

    context = {
        'categoryName': categoryName,
        'posts': category.post_set.all()
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