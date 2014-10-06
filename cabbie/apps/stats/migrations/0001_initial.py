# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LocationDataAccess',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc704\uce58\uc815\ubcf4 \uc811\uadfc\ub85c\uadf8',
                'verbose_name_plural': '\uc704\uce58\uc815\ubcf4 \uc811\uadfc\ub85c\uadf8',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
