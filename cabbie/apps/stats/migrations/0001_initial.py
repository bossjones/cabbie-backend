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
                ('user', models.ForeignKey(verbose_name='\uc811\uadfc\ud55c \uc0ac\uc6a9\uc790', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc704\uce58\uc815\ubcf4 \uc811\uadfc\ub85c\uadf8',
                'verbose_name_plural': '\uc704\uce58\uc815\ubcf4 \uc811\uadfc\ub85c\uadf8',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LocationDataNotice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('purpose', models.CharField(max_length=100, verbose_name='\ubaa9\uc801')),
                ('noticer', models.ForeignKey(verbose_name='\ucde8\uae09\uc790', to=settings.AUTH_USER_MODEL)),
                ('requester', models.ForeignKey(verbose_name='\uc694\uccad\uc790', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc704\uce58\uc815\ubcf4 \uc5f4\ub78c\ubc0f\uace0\uc9c0\ub0b4\uc5ed',
                'verbose_name_plural': '\uc704\uce58\uc815\ubcf4 \uc5f4\ub78c\ubc0f\uace0\uc9c0\ub0b4\uc5ed',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LocationDataProvide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('provider_type', models.CharField(max_length=20, verbose_name='\ucde8\ub4dd\uacbd\ub85c')),
                ('service', models.CharField(max_length=20, verbose_name='\uc81c\uacf5\uc11c\ube44\uc2a4')),
                ('providee', models.ForeignKey(verbose_name='\uc81c\uacf5\ubc1b\uc740\uc790', blank=True, to=settings.AUTH_USER_MODEL)),
                ('provider', models.ForeignKey(verbose_name='\uc81c\uacf5\ud55c\uc790', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc704\uce58\uc815\ubcf4 \uc774\uc6a9\uc81c\uacf5\ub0b4\uc5ed',
                'verbose_name_plural': '\uc704\uce58\uc815\ubcf4 \uc774\uc6a9\uc81c\uacf5\ub0b4\uc5ed',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
