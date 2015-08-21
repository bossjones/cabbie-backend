# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0009_auto_20150619_1806'),
    ]

    operations = [
        migrations.AlterField(
            model_name='favorite',
            name='passenger',
            field=models.ForeignKey(related_name='favorites', verbose_name='\uc2b9\uac1d', to='account.Passenger'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='request',
            name='approval',
            field=models.ForeignKey(related_name='approved_request', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2b9\uc778\ub41c \ubc30\ucc28', blank=True, to='drive.Ride', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='request',
            name='passenger',
            field=models.ForeignKey(related_name='requests', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2b9\uac1d', to='account.Passenger', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='request',
            name='source_province',
            field=models.ForeignKey(related_name='requests', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ucf5c\uc694\uccad \uc9c0\uc5ed', blank=True, to='drive.Province', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ride',
            name='driver',
            field=models.ForeignKey(related_name='rides', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uae30\uc0ac', blank=True, to='account.Driver', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ride',
            name='passenger',
            field=models.ForeignKey(related_name='rides', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2b9\uac1d', to='account.Passenger', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ridehistory',
            name='driver',
            field=models.ForeignKey(related_name='ride_histories', verbose_name='\uae30\uc0ac', blank=True, to='account.Driver', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='ridehistory',
            name='ride',
            field=models.ForeignKey(related_name='histories', verbose_name='\ubc30\ucc28', to='drive.Ride'),
            preserve_default=True,
        ),
    ]
