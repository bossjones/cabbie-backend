# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import tinymce.models
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('notice', '0006_auto_20151002_1507'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppExplanation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this object should be treated as active. Unselect this instead of deleting.', db_index=True, verbose_name=b'active')),
                ('inactive_note', models.CharField(max_length=1000, blank=True)),
                ('active_changed_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('explanation_type', models.CharField(default=b'promotion_code', unique=True, max_length=15, verbose_name='\ud0c0\uc785', choices=[(b'promotion_code', '\ud504\ub85c\ubaa8\uc158\ucf54\ub4dc'), (b'refund', '\ud658\uae09')])),
                ('content', tinymce.models.HTMLField(verbose_name='\ub0b4\uc6a9')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'verbose_name': '\uc571\ub0b4\uc124\uba85',
                'verbose_name_plural': '\uc571\ub0b4\uc124\uba85',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
