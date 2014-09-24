# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DriverBill',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('target_month', models.CharField(help_text='e.g. 201409', max_length=6)),
                ('amount', models.PositiveIntegerField()),
                ('driver', models.ForeignKey(to='account.Driver')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \uc0ac\uc6a9\ub8cc',
                'verbose_name_plural': '\uae30\uc0ac \uc0ac\uc6a9\ub8cc',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DriverCoupon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('coupon_type', models.CharField(db_index=True, max_length=100, choices=[(b'gas', 'LPG \ucda9\uc804\uad8c')])),
                ('amount', models.PositiveIntegerField(null=True, blank=True)),
                ('serial_number', models.CharField(max_length=100, blank=True)),
                ('driver', models.ForeignKey(to='account.Driver')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \ucfe0\ud3f0',
                'verbose_name_plural': '\uae30\uc0ac \ucfe0\ud3f0',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('user_object_id', models.PositiveIntegerField()),
                ('transaction_type', models.CharField(db_index=True, max_length=100, choices=[(b'mileage', '\ub9c8\uc77c\ub9ac\uc9c0'), (b'return', '\ud658\uae09'), (b'recommend', '\ucd94\ucc9c'), (b'recommended', '\ud53c\ucd94\ucc9c'), (b'grant', '\uc9c0\uae09')])),
                ('amount', models.IntegerField()),
                ('note', models.CharField(max_length=1000, blank=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\ud3ec\uc778\ud2b8 \uc0ac\uc6a9\ub0b4\uc5ed',
                'verbose_name_plural': '\ud3ec\uc778\ud2b8 \uc0ac\uc6a9\ub0b4\uc5ed',
            },
            bases=(cabbie.common.models.IncrementMixin, cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
