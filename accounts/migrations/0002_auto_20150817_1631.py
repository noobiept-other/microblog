# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='privatemessage',
            options={'ordering': ['-date_created']},
        ),
        migrations.AddField(
            model_name='privatemessage',
            name='has_been_read',
            field=models.BooleanField(default=False),
        ),
    ]
