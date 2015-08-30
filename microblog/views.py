from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count

import re

from microblog import utilities
from microblog.models import Post, Category


def home( request ):
    """
        Show the latest posts, either from all the users (if there's no one logged in), or from the users you're following.
    """
    if request.user.is_authenticated():
        following = request.user.following.all()
        posts = Post.objects.filter( user__in= following ).order_by( '-date_created' )

    else:
        posts = Post.objects.all()

    paginator = Paginator( posts, 10 )
    page = request.GET.get( 'page' )

    try:
        paginatedPosts = paginator.page( page )

    except PageNotAnInteger:
        paginatedPosts = paginator.page( 1 )  # first page

    except EmptyPage:
        paginatedPosts = paginator.page( paginator.num_pages )  # last page


    context = {
        'posts': paginatedPosts
    }

    utilities.get_messages( request, context )

    return render( request, 'home.html', context )


@login_required
def add_post( request ):
    """
        Add a new post.
        It can be an independent post, or a reply to another post (known by the 'postIdentifier' argument).

        Requires a POST request with the following arguments:
            - text
            - image (optional)
            - postIdentifier (optional)
    """
    if not request.method == 'POST':
        return HttpResponseNotAllowed( [ 'POST' ] )

        # check if this is a reply to another post or not, by trying to obtain the parent post object
    postIdentifier = request.POST.get( 'postIdentifier' )

    if postIdentifier:
        try:
            parent = Post.objects.get( identifier= postIdentifier )

        except Post.DoesNotExist:
            parent = None

    else:
        parent = None


    text = request.POST.get( 'text' )

    if not text:
        return HttpResponseBadRequest( "Need a 'text' argument." )

    categories = re.findall( r'#(\w+)', text )
    image = request.FILES.get( 'image' )

    if parent:
        post = Post.objects.create( user= request.user, text= text, image= image, reply_to= parent )

    else:
        post = Post.objects.create( user= request.user, text= text, image= image )


    for category in categories:

        try:
            categoryElement = Category.objects.get( name= category )

        except Category.DoesNotExist:
            categoryElement = Category.objects.create( name= category )

        post.categories.add( categoryElement )


    return JsonResponse({ 'url': post.get_url() })


@login_required
def remove_post( request ):
    """
        Remove a post.

        Requires a POST request with the following arguments:
            - postIdentifier
    """
    if not request.method == 'POST':
        return HttpResponseNotAllowed( [ 'POST' ] )

    postIdentifier = request.POST.get( 'postIdentifier' )

    if not postIdentifier:
        return HttpResponseBadRequest( "Need a 'postIdentifier' argument." )

    try:
        post = request.user.posts.get( identifier= postIdentifier )

    except Post.DoesNotExist:
        return HttpResponseBadRequest( "Invalid 'postIdentifier' argument." )

    post.delete()

    nextUrl = request.GET.get( 'next' )

    if not nextUrl:
        nextUrl = reverse( 'home' )

    utilities.add_message( request, 'Message removed!' )

    return JsonResponse({ 'url': nextUrl })


@login_required
def set_follow( request, username ):
    """
        Follow or un-follow an user.
    """
    userModel = get_user_model()

    if username == request.user.username:
        return HttpResponseBadRequest( "Can't follow yourself." )

    try:
        userToFollow = userModel.objects.get( username= username )

    except userModel.DoesNotExist:
        raise Http404( "User doesn't exist." )


        # figure out if we're following or un-following
    try:
        request.user.following.get( username= username )

    except userModel.DoesNotExist:
        request.user.following.add( userToFollow )

        utilities.add_message( request, '{} followed'.format( userToFollow ) )

    else:
        request.user.following.remove( userToFollow )

        utilities.add_message( request, '{} un-followed'.format( userToFollow ) )

    nextUrl = request.GET.get( 'next' )

    if nextUrl:
        return HttpResponseRedirect( nextUrl )

    else:
        return HttpResponseRedirect( reverse( 'home' ) )


def show_category( request, categoryName ):
    """
        Show all the posts of the given category.
    """
    try:
        category = Category.objects.get( name= categoryName )

    except Category.DoesNotExist:
        raise Http404( "Category doesn't exist." )

    allPosts = category.posts.all().order_by( '-date_created' )
    paginator = Paginator( allPosts, 5 )
    page = request.GET.get( 'page' )

    try:
        posts = paginator.page( page )

    except PageNotAnInteger:
        posts = paginator.page( 1 )  # first page

    except EmptyPage:
        posts = paginator.page( paginator.num_pages )  # last page

    context = {
        'categoryName': categoryName,
        'posts': posts
    }
    utilities.get_messages( request, context )

    return render( request, 'category.html', context )


def show_people( request ):
    """
        If there's a user logged in, show a list of users that can be followed, otherwise just show a list of all the users.
    """
    userModel = get_user_model()

    if request.user.is_authenticated():
        following = []

            # don't consider the people you're already following
        for people in request.user.following.all():
            following.append( people.username )

            # and yourself as well
        following.append( request.user.username )

        allUsers = userModel.objects.exclude( username__in= following )

    else:
        allUsers = userModel.objects.all()

    paginator = Paginator( allUsers, 10 )
    page = request.GET.get( 'page' )

    try:
        users = paginator.page( page )

    except PageNotAnInteger:
        users = paginator.page( 1 )  # first page

    except EmptyPage:
        users = paginator.page( paginator.num_pages )  # last page

    context = {
        'users': users
    }
    utilities.get_messages( request, context )

    return render( request, 'people.html', context )


def show_categories( request ):
    """
        Show a list with all the non-empty categories.
    """
        # show only non-empty categories
    allCategories = Category.objects.annotate( posts_count= Count( 'posts' ) ).filter( posts_count__gt= 0 ).order_by( '-posts_count' )

    paginator = Paginator( allCategories, 10 )
    page = request.GET.get( 'page' )

    try:
        categories = paginator.page( page )

    except PageNotAnInteger:
        categories = paginator.page( 1 )  # first page

    except EmptyPage:
        categories = paginator.page( paginator.num_pages )  # last page

    context = {
        'categories': categories
    }

    return render( request, 'categories.html', context )


def show_post( request, identifier ):
    """
        Shows the post plus its replies.
        If this post was a reply to other post, then show the parent post and its replies as well.
    """
    try:
        post = Post.objects.get( identifier= identifier )

    except Post.DoesNotExist:
        utilities.add_message( request, "Couldn't open the message.", utilities.MessageType.error )
        return HttpResponseRedirect( reverse( 'home' ) )

    posts = []
    replies = []
    parent = post.reply_to

    if parent:
        posts.append( parent )

        for reply in parent.replies.all().order_by( 'date_created' ):
            posts.append( reply )

            if reply == post:
                replies.extend( post.replies.all().order_by( 'date_created' ) )

    else:
        posts.append( post )
        replies.extend( post.replies.all().order_by( 'date_created' ) )

    context = {
        'posts': posts,
        'replies': replies,
        'selected_post': post,
    }

    return render( request, 'show_post.html', context )


def search( request ):
    """
        Search for a post, user or a category.
    """
    if not request.method == 'POST':
        return HttpResponseNotAllowed( [ 'POST' ] )

    searchText = request.POST.get( 'SearchText' )
    context = {
        'search': searchText
    }

    if not searchText or len( searchText ) < 3:
        utilities.add_message( request, 'The search text needs to have 3 or more characters.' )

    else:
        userModel = get_user_model()

        people = userModel.objects.filter( username__icontains= searchText )
        categories = Category.objects.filter( name__icontains= searchText )
        posts = Post.objects.filter( text__icontains= searchText )

        context.update({
            'people': people,
            'categories': categories,
            'posts': posts
        })

    utilities.get_messages( request, context )

    return render( request, 'search.html', context )