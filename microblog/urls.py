from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',

    url( r'^$', 'microblog.views.home', name= 'home' ),

    url( r'^post$', 'microblog.views.post_message', name= 'post' ),
    url( r'^follow/(?P<username>\w+)$', 'microblog.views.set_follow', name= 'follow' ),
    url( r'^category/(?P<categoryName>\w+)$', 'microblog.views.show_category', name= 'show_category' ),
    url( r'^people$', 'microblog.views.show_people', name= 'people' ),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url( r'^accounts/', include( 'accounts.urls', namespace= 'accounts', app_name= 'accounts' ) ),

    url( r'^admin/', include( admin.site.urls ) ),
)
