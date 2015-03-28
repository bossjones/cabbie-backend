# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields
import django.contrib.gis.db.models.fields
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '__first__'),
        ('drive', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('source_location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\ucd9c\ubc1c\uc9c0 \uc88c\ud45c')),
                ('state', models.CharField(max_length=50, verbose_name='\uc0c1\ud0dc', choices=[(b'standby', 'standby'), (b'approved', 'approved'), (b'rejected', 'rejected')])),
                ('contacts', cabbie.common.fields.JSONField(default=b'[]', verbose_name='\ubcf4\ub0b8\uae30\uc0ac \ub9ac\uc2a4\ud2b8')),
                ('rejects', cabbie.common.fields.JSONField(default=b'[]', verbose_name='\uac70\uc808\uae30\uc0ac \ub9ac\uc2a4\ud2b8')),
                ('approval', models.ForeignKey(verbose_name='\uc2b9\uc778\ub41c \ubc30\ucc28', blank=True, to='drive.Ride', null=True)),
                ('passenger', models.ForeignKey(verbose_name='\uc2b9\uac1d', to='account.Passenger')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\ubc30\ucc28 \uc694\uccad',
                'verbose_name_plural': '\ubc30\ucc28 \uc694\uccad',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='ride',
            name='reason',
            field=models.CharField(max_length=20, verbose_name='\uac70\uc808\uc774\uc720', choices=[(b'immediate', 'immediate'), (b'timeout', 'timeout'), (b'after', 'after'), (b'waiting', 'waiting'), (b'unshown', 'unshown')]),
        ),
    ]
