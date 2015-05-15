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
            name='Education',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('name', models.CharField(max_length=20, verbose_name='\uad50\uc721\uba85')),
                ('place', models.CharField(max_length=20, verbose_name='\uc7a5\uc18c')),
                ('started_at', models.DateTimeField(verbose_name='\uad50\uc721\uc2dc\uac04')),
                ('lecturer', models.CharField(max_length=20, verbose_name='\uac15\uc0ac')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uad50\uc721',
                'verbose_name_plural': '\uad50\uc721',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
