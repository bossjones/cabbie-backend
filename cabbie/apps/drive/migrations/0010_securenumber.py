# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.db.models.deletion
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0009_auto_20150619_1806'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecureNumber',
            fields=[
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('phone', models.CharField(max_length=20, serialize=False, verbose_name='\uc548\uc2ec\ubc88\ud638', primary_key=True)),
                ('state', models.CharField(max_length=10, verbose_name='\uc0c1\ud0dc', choices=[(b'acquired', 'acquired'), (b'released', 'released')])),
                ('role', models.CharField(blank=True, max_length=1, null=True, verbose_name='\uc18c\uc720\uc790\ud0c0\uc785', choices=[(b'd', 'd'), (b'p', 'p')])),
                ('ride', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ubc30\ucc28', blank=True, to='drive.Ride', null=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc548\uc2ec\ubc88\ud638',
                'verbose_name_plural': '\uc548\uc2ec\ubc88\ud638',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
