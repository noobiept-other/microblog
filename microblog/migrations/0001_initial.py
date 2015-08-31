# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(max_length=200)),
                ('image', models.FileField(upload_to='images/%Y_%m_%d', blank=True)),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('identifier', models.UUIDField(default=uuid.uuid4, unique=True)),
                ('categories', models.ManyToManyField(to='microblog.Category', related_name='posts')),
                ('reply_to', models.ForeignKey(blank=True, null=True, to='microblog.Post', related_name='replies')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='posts')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
    ]
