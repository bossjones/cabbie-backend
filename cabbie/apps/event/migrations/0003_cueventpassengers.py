# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_driverlocation'),
        ('event', '0002_auto_20151029_1615'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuEventPassengers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('code', models.CharField(max_length=10, verbose_name='\ucf54\ub4dc')),
                ('is_gift_sent', models.BooleanField(default=False, verbose_name='\uae30\ud504\ud2f0\ucf58 \ubc1c\uc1a1\uc5ec\ubd80')),
                ('gift_sent_at', models.DateTimeField(null=True, verbose_name='\uae30\ud504\ud2f0\ucf58 \ubc1c\uc1a1\uc2dc\uac01', blank=True)),
                ('passenger', models.OneToOneField(null=True, blank=True, to='account.Passenger')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'verbose_name': 'CU \ucf54\ub4dc\uc785\ub825 \uc2b9\uac1d',
                'verbose_name_plural': 'CU \ucf54\ub4dc\uc785\ub825 \uc2b9\uac1d',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
