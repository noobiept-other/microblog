from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

import re

from microblog import utilities
from microblog.models import Post, Category


def home( request ):

    if request.user.is_authenticated():
        following = request.user.following.all()
        posts = Post.objects.filter( user__in= following ).order_by( '-date_created' )

    else:
        posts = Post.objects.all()

    paginator = Paginator( posts, 5 )
    page = request.GET.get( 'page' )

    try:
        messages = paginator.page( page )

    except PageNotAnInteger:
        messages = paginator.page( 1 )  # first page

    except EmptyPage:
        messages = paginator.page( paginator.num_pages )  # last page


    context = {
        'messages': messages
    }

    utilities.get_message( request, context )

    return render( request, 'home.html', context )


@login_required
def post_message( request ):
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
        message = Post.objects.create( user= request.user, text= text, image= image, reply_to= parent )

    else:
        message = Post.objects.create( user= request.user, text= text, image= image )


    for category in categories:

        try:
            categoryElement = Category.objects.get( name= category )

        except Category.DoesNotExist:
            categoryElement = Category.objects.create( name= category )

        message.categories.add( categoryElement )


    return JsonResponse({ 'url': message.get_url() })


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

    nextUrl = request.GET.get( 'next' )

    if nextUrl:
        return HttpResponseRedirect( nextUrl )

    else:
        return HttpResponseRedirect( reverse( 'home' ) )


def show_category( request, categoryName ):

    try:
        category = Category.objects.get( name= categoryName )

    except Category.DoesNotExist:
        raise Http404( "Category doesn't exist." )

    allMessages = category.post_set.all().order_by( '-date_created' )
    paginator = Paginator( allMessages, 5 )
    page = request.GET.get( 'page' )

    try:
        messages = paginator.page( page )

    except PageNotAnInteger:
        messages = paginator.page( 1 )  # first page

    except EmptyPage:
        messages = paginator.page( paginator.num_pages )  # last page

    context = {
        'categoryName': categoryName,
        'messages': messages
    }

    return render( request, 'category.html', context )


def show_people( request ):

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
    utilities.get_message( request, context )

    return render( request, 'people.html', context )


def show_categories( request ):

    categories = Category.objects.all()

    context = {
        'categories': categories
    }

    return render( request, 'categories.html', context )


def show_message( request, identifier ):

    try:
        post = Post.objects.get( identifier= identifier )

    except Post.DoesNotExist:
        raise Http404( "Invalid identifier." )

    messages = []
    replies = []
    parent = post.reply_to

    if parent:
        messages.append( parent )

        for reply in parent.replies.all().order_by( 'date_created' ):
            messages.append( reply )

            if reply == post:
                replies.extend( post.replies.all().order_by( 'date_created' ) )

    else:
        messages.append( post )
        replies.extend( post.replies.all().order_by( 'date_created' ) )

    context = {
        'messages': messages,
        'replies': replies,
        'selected_message': post,
    }

    return render( request, 'show_message.html', context )


def search( request ):
    if not request.method == 'POST':
        return HttpResponseNotAllowed( [ 'POST' ] )

    searchText = request.POST.get( 'SearchText' )
    context = {
        'search': searchText
    }

    if not searchText or len( searchText ) < 3:
        utilities.set_message( request, 'The search text needs to have 3 or more characters.' )

    else:
        userModel = get_user_model()

        people = userModel.objects.filter( username__icontains= searchText )
        categories = Category.objects.filter( name__icontains= searchText )
        messages = Post.objects.filter( text__icontains= searchText )

        context.update({
            'people': people,
            'categories': categories,
            'messages': messages
        })

    utilities.get_message( request, context )

    return render( request, 'search.html', context )