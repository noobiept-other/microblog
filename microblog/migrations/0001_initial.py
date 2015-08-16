# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.SlugField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('text', models.TextField(max_length=200)),
                ('image', models.FileField(blank=True, upload_to='images/%Y_%m_%d')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('position', models.IntegerField()),
                ('identifier', models.CharField(unique=True, default=uuid.uuid4, max_length=40)),
                ('categories', models.ManyToManyField(to='microblog.Category')),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('text', models.TextField(max_length=200)),
                ('image', models.FileField(blank=True, upload_to='images/%Y_%m_%d')),
                ('date_created', models.DateTimeField(default=django.utils.timezone.now)),
                ('identifier', models.CharField(unique=True, default=uuid.uuid4, max_length=40)),
                ('categories', models.ManyToManyField(to='microblog.Category')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-date_created'],
            },
        ),
        migrations.AddField(
            model_name='post',
            name='thread',
            field=models.ForeignKey(to='microblog.Thread'),
        ),
        migrations.AddField(
            model_name='post',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
