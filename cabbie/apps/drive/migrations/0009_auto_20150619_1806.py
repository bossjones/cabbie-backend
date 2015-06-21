# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0008_auto_20150512_1526'),
    ]

    operations = [
        migrations.CreateModel(
            name='Province',
            fields=[
                ('name', models.CharField(max_length=20, serialize=False, verbose_name='\uc2dc\ub3c4', primary_key=True)),
            ],
            options={
                'verbose_name': '\uc2dc\ub3c4',
                'verbose_name_plural': '\uc2dc\ub3c4',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='request',
            name='source_province',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ucf5c\uc694\uccad \uc9c0\uc5ed', blank=True, to='drive.Province', null=True),
            preserve_default=True,
        ),
    ]
