# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.contrib.gis.db.models.fields
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '__first__'),
        ('drive', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326, verbose_name='\uc88c\ud45c')),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', blank=True, to='account.Driver', null=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac\uc704\uce58',
                'verbose_name_plural': '\uae30\uc0ac\uc704\uce58',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.AlterField(
            model_name='ride',
            name='state',
            field=models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc', choices=[(b'requested', 'requested'), (b'approved', 'approved'), (b'rejected', 'rejected'), (b'canceled', 'canceled'), (b'disconnected', 'disconnected'), (b'arrived', 'arrived'), (b'boarded', 'boarded'), (b'completed', 'completed'), (b'rated', 'rated')]),
        ),
        migrations.AlterField(
            model_name='ridehistory',
            name='state',
            field=models.CharField(max_length=100, verbose_name='\uc0c1\ud0dc', choices=[(b'requested', 'requested'), (b'approved', 'approved'), (b'rejected', 'rejected'), (b'canceled', 'canceled'), (b'disconnected', 'disconnected'), (b'arrived', 'arrived'), (b'boarded', 'boarded'), (b'completed', 'completed'), (b'rated', 'rated')]),
        ),
    ]
