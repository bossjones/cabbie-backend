# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('kpi', '0002_passengerkpimodel_ride_rate_sum'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverKpiModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('start_filter', models.DateTimeField(null=True, verbose_name='\uc2dc\uc791\uc77c')),
                ('end_filter', models.DateTimeField(null=True, verbose_name='\uc885\ub8cc\uc77c')),
                ('subscriber', models.PositiveIntegerField(verbose_name='\uc2e0\uaddc\uac00\uc785\uc790')),
                ('rate_sum_of_educated', models.PositiveIntegerField(verbose_name='\uc815\uaddc\uad50\uc721 \uc774\uc218 \uae30\uc0ac \ud3c9\uc810\ud569\uacc4')),
                ('rate_count_of_educated', models.FloatField(verbose_name='\uc815\uaddc\uad50\uc721 \uc774\uc218 \uae30\uc0ac \ud3c9\uc810\uc218')),
                ('rate_sum_of_uneducated', models.FloatField(verbose_name='\uad50\uc721 \ube44\uc774\uc218 \uae30\uc0ac \ud3c9\uc810\ud569\uacc4')),
                ('rate_count_of_uneducated', models.FloatField(verbose_name='\uad50\uc721 \ube44\uc774\uc218 \uae30\uc0ac \ud3c9\uc810\uc218')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac KPI',
                'verbose_name_plural': '\uae30\uc0ac KPI',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
