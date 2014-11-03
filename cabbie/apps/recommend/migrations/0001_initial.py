# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recommend',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('recommender_object_id', models.PositiveIntegerField()),
                ('recommendee_object_id', models.PositiveIntegerField()),
                ('recommend_type', models.CharField(db_index=True, max_length=100, verbose_name='\ucd94\ucc9c \uc885\ub958', choices=[(b'p2p', '\uc2b9\uac1d to \uc2b9\uac1d'), (b'd2d', '\uae30\uc0ac to \uae30\uc0ac'), (b'd2p', '\uae30\uc0ac to \uc2b9\uac1d')])),
                ('recommendee_content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('recommender_content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\ucd94\ucc9c',
                'verbose_name_plural': '\ucd94\ucc9c',
            },
            bases=(cabbie.common.models.IncrementMixin, cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
