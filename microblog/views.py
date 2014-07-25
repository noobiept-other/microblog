from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model

import microblog.utilities as utilities
from microblog.forms import PostForm
from microblog.models import Post

@login_required( login_url= 'accounts:login' )
def home( request ):

    posts = request.user.post_set.all()[ :5 ]

    context = {
        'posts': posts
    }

    utilities.get_message( request, context )

    return render( request, 'home.html', context )


@login_required( login_url= 'accounts:login' )
def post_message( request ):

    if request.method == 'POST':

        form = PostForm( request.POST )

        if form.is_valid():

            text = form.cleaned_data[ 'text' ]

            post = Post( user= request.user, text= text )
            post.save()

            return HttpResponseRedirect( reverse( 'home' ) )

    else:
        form = PostForm()

    context = {
        'form': form
    }

    return render( request, 'post.html', context )