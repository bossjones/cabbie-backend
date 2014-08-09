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
            name='Ride',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, choices=[(b'requested', 'requested'), (b'approved', 'approved'), (b'rejected', 'rejected'), (b'canceled', 'canceled'), (b'disconnected', 'disconnected'), (b'arrived', 'arrived'), (b'boarded', 'boarded'), (b'completed', 'completed'), (b'rated', 'rated')])),
                ('source', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('destination', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('rating', models.PositiveIntegerField(null=True, blank=True)),
                ('comment', models.CharField(max_length=100, blank=True)),
                ('driver', models.ForeignKey(blank=True, to='account.Driver', null=True)),
                ('passenger', models.ForeignKey(to='account.Passenger')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RideHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('state', models.CharField(max_length=100, choices=[(b'requested', 'requested'), (b'approved', 'approved'), (b'rejected', 'rejected'), (b'canceled', 'canceled'), (b'disconnected', 'disconnected'), (b'arrived', 'arrived'), (b'boarded', 'boarded'), (b'completed', 'completed'), (b'rated', 'rated')])),
                ('passenger_location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('driver_location', django.contrib.gis.db.models.fields.PointField(srid=4326, null=True, blank=True)),
                ('data', cabbie.common.fields.JSONField(default=b'{}')),
                ('driver', models.ForeignKey(blank=True, to='account.Driver', null=True)),
                ('ride', models.ForeignKey(to='drive.Ride')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
