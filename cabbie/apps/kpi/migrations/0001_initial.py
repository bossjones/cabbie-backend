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
            name='PassengerKpiModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('start_filter', models.DateTimeField(null=True, verbose_name='\uc2dc\uc791\uc77c')),
                ('end_filter', models.DateTimeField(null=True, verbose_name='\uc885\ub8cc\uc77c')),
                ('subscriber', models.PositiveIntegerField(verbose_name='\uc2e0\uaddc\uac00\uc785\uc790')),
                ('active_user', models.PositiveIntegerField(verbose_name='Active User')),
                ('ride_requested', models.PositiveIntegerField(verbose_name='\ucf5c\uc694\uccad')),
                ('ride_approved', models.PositiveIntegerField(verbose_name='\uc218\ub77d')),
                ('ride_canceled', models.PositiveIntegerField(verbose_name='\uc2b9\uac1d\ucde8\uc18c')),
                ('ride_rejected', models.PositiveIntegerField(verbose_name='\uae30\uc0ac\uac70\uc808')),
                ('ride_completed', models.PositiveIntegerField(verbose_name='\uc6b4\ud589\uc644\ub8cc')),
                ('ride_rated', models.PositiveIntegerField(verbose_name='\ud3c9\uac00\uc644\ub8cc')),
                ('ride_satisfied', models.PositiveIntegerField(verbose_name='4.5\uc774\uc0c1')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc2b9\uac1d KPI',
                'verbose_name_plural': '\uc2b9\uac1d KPI',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
