# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20151002_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverLocation',
            fields=[
                ('driver', models.OneToOneField(primary_key=True, serialize=False, to='account.Driver')),
                ('activated', models.BooleanField(default=False, verbose_name='\ud65c\uc131\ud654\uc5ec\ubd80')),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\uc88c\ud45c')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('parse_object_id', models.CharField(max_length=20, verbose_name='Parse object ID')),
            ],
            options={
                'verbose_name': '\uae30\uc0ac\uc704\uce58',
                'verbose_name_plural': '\uae30\uc0ac\uc704\uce58',
            },
            bases=(models.Model,),
        ),
    ]
