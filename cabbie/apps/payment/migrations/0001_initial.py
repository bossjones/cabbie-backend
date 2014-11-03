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
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('target_month', models.CharField(help_text='e.g. 201409', max_length=6)),
                ('amount', models.PositiveIntegerField(verbose_name='\uae08\uc561')),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
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
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('coupon_type', models.CharField(default=b'gas', max_length=100, verbose_name='\ucfe0\ud3f0 \uc885\ub958', db_index=True, choices=[(b'gas', 'LPG \ucda9\uc804\uad8c')])),
                ('amount', models.PositiveIntegerField(null=True, verbose_name='\uae08\uc561', blank=True)),
                ('serial_number', models.CharField(max_length=100, verbose_name='\ucfe0\ud3f0\uc77c\ub828\ubc88\ud638', blank=True)),
                ('is_processed', models.BooleanField(default=False, verbose_name='\uc9c0\uae09\uc644\ub8cc\uc5ec\ubd80')),
                ('processed_at', models.DateTimeField(null=True, verbose_name='\uc9c0\uae09\uc2dc\uc810', blank=True)),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
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
            name='DriverReturn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('amount', models.PositiveIntegerField(default=0, verbose_name='\ud658\uae09\uc561')),
                ('is_requested', models.BooleanField(default=False, verbose_name='\ud658\uae09\uc694\uccad\uc5ec\ubd80')),
                ('is_processed', models.BooleanField(default=False, verbose_name='\ud658\uae09\uc644\ub8cc\uc5ec\ubd80')),
                ('processed_at', models.DateTimeField(null=True, verbose_name='\ud658\uae09\uc2dc\uc810', blank=True)),
                ('user', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \ud658\uae09\uae08',
                'verbose_name_plural': '\uae30\uc0ac \ud658\uae09\uae08',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='PassengerReturn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('amount', models.PositiveIntegerField(default=0, verbose_name='\ud658\uae09\uc561')),
                ('is_requested', models.BooleanField(default=False, verbose_name='\ud658\uae09\uc694\uccad\uc5ec\ubd80')),
                ('is_processed', models.BooleanField(default=False, verbose_name='\ud658\uae09\uc644\ub8cc\uc5ec\ubd80')),
                ('processed_at', models.DateTimeField(null=True, verbose_name='\ud658\uae09\uc2dc\uc810', blank=True)),
                ('user', models.ForeignKey(verbose_name='\uc2b9\uac1d', to='account.Passenger')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc2b9\uac1d \ud658\uae09\uae08',
                'verbose_name_plural': '\uc2b9\uac1d \ud658\uae09\uae08',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('transaction_type', models.CharField(db_index=True, max_length=100, verbose_name='\uc885\ub958', choices=[(b'mileage', '\ub9c8\uc77c\ub9ac\uc9c0'), (b'recommend', '\ucd94\ucc9c'), (b'recommended', '\ud53c\ucd94\ucc9c'), (b'grant', '\uc9c0\uae09'), (b'return', '\ud658\uae09')])),
                ('amount', models.IntegerField(verbose_name='\uae08\uc561')),
                ('note', models.CharField(max_length=1000, verbose_name='\uba54\ubaa8', blank=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\ud3ec\uc778\ud2b8 \uc774\ub825',
                'verbose_name_plural': '\ud3ec\uc778\ud2b8 \uc774\ub825',
            },
            bases=(cabbie.common.models.IncrementMixin, cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
    ]
