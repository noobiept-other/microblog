# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('microblog', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thread',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='thread',
            name='user',
        ),
        migrations.RemoveField(
            model_name='post',
            name='position',
        ),
        migrations.RemoveField(
            model_name='post',
            name='thread',
        ),
        migrations.AddField(
            model_name='post',
            name='replies',
            field=models.ForeignKey(to='microblog.Post', null=True, blank=True, related_name='parent'),
        ),
        migrations.AlterField(
            model_name='post',
            name='identifier',
            field=models.UUIDField(unique=True, default=uuid.uuid4),
        ),
        migrations.AlterField(
            model_name='post',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='posts'),
        ),
        migrations.DeleteModel(
            name='Thread',
        ),
    ]
