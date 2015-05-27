# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Affiliation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this object should be treated as active. Unselect this instead of deleting.', db_index=True, verbose_name=b'active')),
                ('inactive_note', models.CharField(max_length=1000, blank=True)),
                ('active_changed_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('image', models.ImageField(height_field=b'image_height', width_field=b'image_width', null=True, upload_to=cabbie.common.models._upload_to, blank=True)),
                ('image_key', models.CharField(max_length=100, blank=True)),
                ('image_width', models.IntegerField(null=True, blank=True)),
                ('image_height', models.IntegerField(null=True, blank=True)),
                ('name', models.CharField(max_length=30, verbose_name='\uc774\ub984')),
                ('certificate_code', models.CharField(max_length=20, verbose_name='\uc778\uc99d\ucf54\ub4dc')),
                ('ride_mileage', models.PositiveIntegerField(default=2000, verbose_name='\ud0d1\uc2b9\ub9c8\uc77c\ub9ac\uc9c0', blank=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc81c\ud734\uc0ac',
                'verbose_name_plural': '\uc81c\ud734\uc0ac',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
