# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
        ('drive', '0001_initial'),
        ('payment', '0001_initial'),
        ('recommend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='recommend',
            field=models.ForeignKey(blank=True, to='recommend.Recommend', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='ride',
            field=models.ForeignKey(blank=True, to='drive.Ride', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='user_content_type',
            field=models.ForeignKey(to='contenttypes.ContentType'),
            preserve_default=True,
        ),
    ]
