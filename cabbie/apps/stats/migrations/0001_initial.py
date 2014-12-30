# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverRideStatDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='\ud69f\uc218')),
                ('ratings', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ud0d1\uc2b9 \ud3c9\uc810')),
                ('year', models.PositiveIntegerField(verbose_name='\ub144')),
                ('month', models.PositiveIntegerField(verbose_name='\uc6d4')),
                ('week', models.PositiveIntegerField(verbose_name='\uc8fc')),
                ('day', models.PositiveIntegerField(verbose_name='\uc77c')),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \uc77c\ubcc4 \uc5c5\ubb34\ud1b5\uacc4',
                'verbose_name_plural': '\uae30\uc0ac \uc77c\ubcc4 \uc5c5\ubb34\ud1b5\uacc4',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='driverridestatday',
            unique_together=set([(b'driver', b'year', b'month', b'week', b'day', b'state')]),
        ),
        migrations.CreateModel(
            name='DriverRideStatMonth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='\ud69f\uc218')),
                ('ratings', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ud0d1\uc2b9 \ud3c9\uc810')),
                ('year', models.PositiveIntegerField(verbose_name='\ub144')),
                ('month', models.PositiveIntegerField(verbose_name='\uc6d4')),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \uc6d4\ubcc4 \uc5c5\ubb34\ud1b5\uacc4',
                'verbose_name_plural': '\uae30\uc0ac \uc6d4\ubcc4 \uc5c5\ubb34\ud1b5\uacc4',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='driverridestatmonth',
            unique_together=set([(b'driver', b'year', b'month', b'state')]),
        ),
        migrations.CreateModel(
            name='DriverRideStatWeek',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc')),
                ('count', models.PositiveIntegerField(default=0, verbose_name='\ud69f\uc218')),
                ('ratings', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ud0d1\uc2b9 \ud3c9\uc810')),
                ('year', models.PositiveIntegerField(verbose_name='\ub144')),
                ('month', models.PositiveIntegerField(verbose_name='\uc6d4')),
                ('week', models.PositiveIntegerField(verbose_name='\uc8fc')),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \uc8fc\ubcc4 \uc5c5\ubb34\ud1b5\uacc4',
                'verbose_name_plural': '\uae30\uc0ac \uc8fc\ubcc4 \uc5c5\ubb34\ud1b5\uacc4',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.AlterUniqueTogether(
            name='driverridestatweek',
            unique_together=set([(b'driver', b'year', b'month', b'week', b'state')]),
        ),
    ]
