"""
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
"""
from django.conf.urls import include, url
from django.conf import settings
from django.contrib import admin

import microblog.views
import accounts.urls


urlpatterns = [

    url( r'^$', microblog.views.home, name= 'home' ),

    url( r'^post/add$', microblog.views.add_post, name= 'add_post' ),
    url( r'^post/remove$', microblog.views.remove_post, name= 'remove_post' ),

    url( r'^follow/(?P<username>\w+)$', microblog.views.set_follow, name= 'follow' ),
    url( r'^category/(?P<categoryName>\w+)$', microblog.views.show_category, name= 'show_category' ),
    url( r'^people$', microblog.views.show_people, name= 'people' ),
    url( r'^categories$', microblog.views.show_categories, name= 'categories' ),
    url( r'^message/(?P<identifier>[\w-]+)$', microblog.views.show_message, name= 'show_message' ),
    url( r'^search$', microblog.views.search, name= 'search' ),

    url( r'^accounts/', include( accounts.urls, namespace= 'accounts', app_name= 'accounts' ) ),
    url( r'^admin/', include( admin.site.urls ) ),
]


if settings.DEBUG:
        # static files (images, css, javascript, etc.)
    urlpatterns += [
        url( r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT } ),
    ]