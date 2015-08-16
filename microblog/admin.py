from django.contrib import admin

from microblog.models import Thread, Post, Category


class ThreadAdmin( admin.ModelAdmin ):

    list_display = ( 'user', 'text', 'date_created' )

admin.site.register( Thread, ThreadAdmin )


class PostAdmin( admin.ModelAdmin ):

    list_display = ( 'thread', 'user', 'text', 'date_created' )

admin.site.register( Post, PostAdmin )


class CategoryAdmin( admin.ModelAdmin ):

    list_display = ( 'name', )

admin.site.register( Category, CategoryAdmin )