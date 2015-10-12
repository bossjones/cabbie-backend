# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0010_auto_20150821_1459'),
    ]

    operations = [
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30, verbose_name='\uc9c0\uc5ed')),
                ('depth', models.PositiveIntegerField(default=0, verbose_name='Depth')),
                ('parent', models.ForeignKey(related_name='childs', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc0c1\uc704\uc9c0\uc5ed', blank=True, to='drive.Region', null=True)),
                ('province', models.ForeignKey(related_name='regions', verbose_name='\uc2dc\ub3c4', to='drive.Province')),
            ],
            options={
                'verbose_name': '\uc9c0\uc5ed',
                'verbose_name_plural': '\uc9c0\uc5ed',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='request',
            name='destination_province',
            field=models.ForeignKey(related_name='destinations', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ub3c4\ucc29\uc9c0 \uc9c0\uc5ed', blank=True, to='drive.Province', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='destination_region1',
            field=models.ForeignKey(related_name='depth1_destination_regions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ub3c4\ucc29\uc9c0 \uc138\ubd80\uc9c0\uc5ed1', blank=True, to='drive.Region', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='destination_region2',
            field=models.ForeignKey(related_name='depth2_destination_regions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ub3c4\ucc29\uc9c0 \uc138\ubd80\uc9c0\uc5ed2', blank=True, to='drive.Region', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='source_region1',
            field=models.ForeignKey(related_name='depth1_request_regions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ucf5c\uc694\uccad \uc138\ubd80\uc9c0\uc5ed1', blank=True, to='drive.Region', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='source_region2',
            field=models.ForeignKey(related_name='depth2_request_regions', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ucf5c\uc694\uccad \uc138\ubd80\uc9c0\uc5ed2', blank=True, to='drive.Region', null=True),
            preserve_default=True,
        ),
    ]
