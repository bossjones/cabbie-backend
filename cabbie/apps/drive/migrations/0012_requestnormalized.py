# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0011_auto_20151012_1415'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestNormalized',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('parent', models.ForeignKey(related_name='childs', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ubd80\ubaa8', blank=True, to='drive.RequestNormalized', null=True)),
                ('ref', models.ForeignKey(related_name='normalized', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ubc30\ucc28\uc694\uccad', to='drive.Request', null=True)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
                'verbose_name': '\ubc30\ucc28 \uc694\uccad Normalization',
                'verbose_name_plural': '\ubc30\ucc28 \uc694\uccad Normalization',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
