from django.conf.urls import patterns, include, url
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url( r'^$', 'microblog.views.home', name= 'home' ),

    url( r'^post$', 'microblog.views.post_message', name= 'post' ),
    url( r'^reply/(?P<threadIdentifier>[\w-]+)$', 'microblog.views.post_message', name= 'reply' ),
    url( r'^follow/(?P<username>\w+)$', 'microblog.views.set_follow', name= 'follow' ),
    url( r'^category/(?P<categoryName>\w+)$', 'microblog.views.show_category', name= 'show_category' ),
    url( r'^people$', 'microblog.views.show_people', name= 'people' ),
    url( r'^categories$', 'microblog.views.show_categories', name= 'categories' ),
    url( r'^message/(?P<identifier>[\w-]+)$', 'microblog.views.show_message', name= 'show_message' ),

    url( r'^followers$', 'accounts.views.show_followers', name= 'show_followers' ),
    url( r'^following$', 'accounts.views.show_following', name= 'show_following' ),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url( r'^accounts/', include( 'accounts.urls', namespace= 'accounts', app_name= 'accounts' ) ),

    url( r'^admin/', include( admin.site.urls ) ),
)


if settings.DEBUG:
        # static files (images, css, javascript, etc.)
    urlpatterns += patterns( '',
        ( r'^media/(?P<path>.*)$', 'django.views.static.serve', {
        'document_root': settings.MEDIA_ROOT } ) )