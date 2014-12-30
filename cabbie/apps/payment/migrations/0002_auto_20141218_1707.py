# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recommend', '0001_initial'),
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='recommend',
            field=models.ForeignKey(verbose_name='\ucd94\ucc9c', blank=True, to='recommend.Recommend', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='ride',
            field=models.ForeignKey(verbose_name='\ucf5c', blank=True, to='drive.Ride', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='transaction',
            name='user',
            field=models.ForeignKey(verbose_name='\uc0ac\uc6a9\uc790', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
