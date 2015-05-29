# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import tinymce.models
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AppPopup',
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
                ('title', models.CharField(max_length=50, verbose_name='\uc81c\ubaa9')),
                ('content', tinymce.models.HTMLField(verbose_name='\ub0b4\uc6a9')),
                ('link', models.URLField(verbose_name='\uc0c1\uc138\ub9c1\ud06c')),
                ('starts_at', models.DateTimeField(null=True, verbose_name='\uc2dc\uc791\uc2dc\uac04', db_index=True)),
                ('ends_at', models.DateTimeField(null=True, verbose_name='\uc885\ub8cc\uc2dc\uac04', db_index=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc571\ud31d\uc5c5',
                'verbose_name_plural': '\uc571\ud31d\uc5c5',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Notice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this object should be treated as active. Unselect this instead of deleting.', db_index=True, verbose_name=b'active')),
                ('inactive_note', models.CharField(max_length=1000, blank=True)),
                ('active_changed_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('title', models.CharField(max_length=50, verbose_name='\uc81c\ubaa9')),
                ('content', tinymce.models.HTMLField(verbose_name='\ub0b4\uc6a9')),
                ('visible_from', models.DateTimeField(verbose_name='\uac8c\uc2dc\uc2dc\uac04')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uacf5\uc9c0\uc0ac\ud56d',
                'verbose_name_plural': '\uacf5\uc9c0\uc0ac\ud56d',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
