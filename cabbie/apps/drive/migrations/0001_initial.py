# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields
import django.contrib.gis.db.models.fields
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('name', models.CharField(max_length=100, verbose_name='\uc774\ub984')),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\uc88c\ud45c')),
                ('address', models.CharField(db_index=True, max_length=1000, verbose_name='\uc8fc\uc18c', blank=True)),
                ('poi', models.CharField(max_length=1000, verbose_name='POI', blank=True)),
                ('passenger', models.ForeignKey(verbose_name='\uc2b9\uac1d', to='account.Passenger')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc990\uaca8\ucc3e\uae30',
                'verbose_name_plural': '\uc990\uaca8\ucc3e\uae30',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Hotspot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(help_text='\uacbd\ub3c4\uc640 \uc704\ub3c4\ub97c \ud55c\uc904\uc529 \uc785\ub825\ud558\uc138\uc694', srid=4326, verbose_name='\uc88c\ud45c')),
                ('address', models.CharField(db_index=True, max_length=1000, verbose_name='\uc8fc\uc18c', blank=True)),
                ('poi', models.CharField(max_length=1000, verbose_name='POI', blank=True)),
                ('ride_count', models.PositiveIntegerField(default=0, verbose_name='\ubc30\ucc28\ud69f\uc218')),
                ('weight', models.IntegerField(help_text='\ub192\uc744\uc218\ub85d \uc0c1\uc704\uc5d0 \ub178\ucd9c\ub429\ub2c8\ub2e4', verbose_name='\uac00\uc911\uce58', db_index=True)),
                ('is_promotion', models.BooleanField(default=True, verbose_name='\ud504\ub85c\ubaa8\uc158')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc778\uae30\uc7a5\uc18c',
                'verbose_name_plural': '\uc778\uae30\uc7a5\uc18c',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Ride',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc', choices=[(b'requested', 'requested'), (b'approved', 'approved'), (b'rejected', 'rejected'), (b'canceled', 'canceled'), (b'disconnected', 'disconnected'), (b'arrived', 'arrived'), (b'boarded', 'boarded'), (b'completed', 'completed'), (b'rated', 'rated')])),
                ('additional_message', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ucd94\uac00\uba54\uc138\uc9c0')),
                ('reason', models.CharField(max_length=20, verbose_name='\uac70\uc808\uc774\uc720', choices=[(b'immediate', '\uc989\uc2dc\uac70\uc808'), (b'timeout', '\uc218\ub77d\uc2dc\uac04\ucd08\uacfc'), (b'after', '\uc218\ub77d\ud6c4 \uac70\uc808'), (b'waiting', '\ub300\uae30\uc911 \uac70\uc808'), (b'unshown', '\uc2b9\uac1d\uc774 \ub098\ud0c0\ub098\uc9c0 \uc54a\uc74c')])),
                ('source', cabbie.common.fields.JSONField(verbose_name='\ucd9c\ubc1c\uc9c0')),
                ('source_location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\ucd9c\ubc1c\uc9c0 \uc88c\ud45c')),
                ('destination', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ub3c4\ucc29\uc9c0')),
                ('destination_location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='\ub3c4\ucc29\uc9c0 \uc88c\ud45c', blank=True)),
                ('charge_type', models.PositiveIntegerField(verbose_name='\ucf5c\ube44', blank=True)),
                ('summary', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\uc694\uc57d')),
                ('ratings_by_category', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\uc0c1\uc138\ud3c9\uc810')),
                ('comment', models.CharField(max_length=100, verbose_name='\ucf54\uba58\ud2b8', blank=True)),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', blank=True, to='account.Driver', null=True)),
                ('passenger', models.ForeignKey(verbose_name='\uc2b9\uac1d', to='account.Passenger')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\ubc30\ucc28',
                'verbose_name_plural': '\ubc30\ucc28',
            },
            bases=(cabbie.common.models.IncrementMixin, cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RideHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc', choices=[(b'requested', 'requested'), (b'approved', 'approved'), (b'rejected', 'rejected'), (b'canceled', 'canceled'), (b'disconnected', 'disconnected'), (b'arrived', 'arrived'), (b'boarded', 'boarded'), (b'completed', 'completed'), (b'rated', 'rated')])),
                ('passenger_location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\uc2b9\uac1d \uc88c\ud45c')),
                ('driver_location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, verbose_name='\uae30\uc0ac \uc88c\ud45c', blank=True)),
                ('data', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ub370\uc774\ud130')),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', blank=True, to='account.Driver', null=True)),
                ('ride', models.ForeignKey(verbose_name='\ubc30\ucc28', to='drive.Ride')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\ubc30\ucc28 \uc774\ub825',
                'verbose_name_plural': '\ubc30\ucc28 \uc774\ub825',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
