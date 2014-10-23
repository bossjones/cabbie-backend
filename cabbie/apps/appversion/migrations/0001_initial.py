# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AndroidDriver',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this object should be treated as active. Unselect this instead of deleting.', db_index=True, verbose_name=b'active')),
                ('inactive_note', models.CharField(max_length=1000, blank=True)),
                ('active_changed_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('version_code', models.PositiveIntegerField(verbose_name='version code')),
                ('version_name', models.CharField(unique=True, max_length=10, verbose_name='version name')),
                ('is_update_required', models.BooleanField(default=False)),
                ('description', models.CharField(max_length=500, verbose_name='description')),
            ],
            options={
                'ordering': [b'-version_code'],
                'verbose_name': '\uc548\ub4dc\ub85c\uc774\ub4dc \uae30\uc0ac\uc571 \ubc84\uc804\uad00\ub9ac',
                'verbose_name_plural': '\uc548\ub4dc\ub85c\uc774\ub4dc \uae30\uc0ac\uc571 \ubc84\uc804\uad00\ub9ac',
            },
            bases=(models.Model,),
        ),
    ]
