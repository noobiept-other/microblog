# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('microblog', '0002_auto_20150822_1658'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='replies',
        ),
        migrations.AddField(
            model_name='post',
            name='reply_to',
            field=models.ForeignKey(null=True, related_name='replies', blank=True, to='microblog.Post'),
        ),
    ]
