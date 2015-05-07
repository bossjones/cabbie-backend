# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('affiliation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliation',
            name='affiliated_at',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='\uc81c\ud734\uc77c\uc790'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='affiliation',
            name='company_code',
            field=models.CharField(default='', max_length=10, verbose_name='\ud68c\uc0ac\ucf54\ub4dc'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='affiliation',
            name='certificate_code',
            field=models.CharField(unique=True, max_length=20, verbose_name='\uc778\uc99d\ucf54\ub4dc'),
        ),
    ]
