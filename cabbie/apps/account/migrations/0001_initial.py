# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cabbie.common.fields
import cabbie.apps.account.models
import cabbie.utils.validator
import django.utils.timezone
from django.conf import settings
import cabbie.common.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_active', models.BooleanField(default=True, help_text=b'Designates whether this object should be treated as active. Unselect this instead of deleting.', db_index=True, verbose_name=b'active')),
                ('inactive_note', models.CharField(max_length=1000, blank=True)),
                ('active_changed_at', models.DateTimeField(default=django.utils.timezone.now, editable=False)),
                ('phone', models.CharField(unique=True, max_length=11, verbose_name='\uc804\ud654\ubc88\ud638', validators=[cabbie.utils.validator.PhoneValidator()])),
                ('name', models.CharField(max_length=30, verbose_name='\uc774\ub984')),
                ('is_staff', models.BooleanField(default=False, verbose_name='\uad00\ub9ac\uc790')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac00\uc785\uc2dc\uae30')),
                ('point', models.PositiveIntegerField(default=0, verbose_name='\ud3ec\uc778\ud2b8')),
                ('recommend_code', models.CharField(default=cabbie.apps.account.models._issue_new_code, unique=True, max_length=10, verbose_name='\ucd94\ucc9c\ucf54\ub4dc')),
                ('is_bot', models.BooleanField(default=False, verbose_name='bot \uc5ec\ubd80')),
                ('last_active_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\ub9c8\uc9c0\ub9c9 \ud65c\ub3d9')),
                ('bank_account', models.CharField(max_length=100, verbose_name='\uacc4\uc88c\uc815\ubcf4', blank=True)),
                ('current_month_board_count', models.PositiveIntegerField(default=0, verbose_name='\ub2f9\uc6d4 \ucf5c\ud69f\uc218')),
                ('previous_month_board_count', models.PositiveIntegerField(default=0, verbose_name='\uc804\uc6d4 \ucf5c\ud69f\uc218')),
                ('board_count', models.PositiveIntegerField(default=0, verbose_name='\ucd1d \ucf5c\ud69f\uc218')),
                ('ride_count', models.PositiveIntegerField(default=0, verbose_name='\ucd1d \ubc30\ucc28\ud69f\uc218')),
                ('driver_recommend_count', models.PositiveIntegerField(default=0, verbose_name='\ucd94\ucc9c\ud69f\uc218 (\uae30\uc0ac)')),
                ('passenger_recommend_count', models.PositiveIntegerField(default=0, verbose_name='\ucd94\ucc9c\ud69f\uc218 (\uc2b9\uac1d)')),
                ('recommended_count', models.PositiveIntegerField(default=0, verbose_name='\ud53c\ucd94\ucc9c\ud69f\uc218')),
                ('groups', models.ManyToManyField(to='auth.Group', verbose_name='groups', blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', verbose_name='user permissions', blank=True)),
            ],
            options={
                'ordering': [b'-date_joined'],
                'verbose_name': '\uc0ac\uc6a9\uc790',
                'verbose_name_plural': '\uc0ac\uc6a9\uc790',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('image', models.ImageField(height_field=b'image_height', width_field=b'image_width', null=True, upload_to=cabbie.common.models._upload_to, blank=True)),
                ('image_key', models.CharField(max_length=100, blank=True)),
                ('image_width', models.IntegerField(null=True, blank=True)),
                ('image_height', models.IntegerField(null=True, blank=True)),
                ('verification_code', models.CharField(max_length=10, verbose_name='\uc778\uc99d\ucf54\ub4dc')),
                ('is_verified', models.BooleanField(default=False, verbose_name='\uc778\uc99d\uc5ec\ubd80')),
                ('is_verification_code_notified', models.BooleanField(default=False, verbose_name='\uc778\uc99d\ucf54\ub4dc \uacf5\uc9c0\uc5ec\ubd80')),
                ('is_accepted', models.BooleanField(default=False, verbose_name='\uc2b9\uc778\uc5ec\ubd80')),
                ('is_freezed', models.BooleanField(default=False, verbose_name='\uc0ac\uc6a9\uc81c\ud55c')),
                ('freeze_note', models.CharField(max_length=1000, verbose_name='\uc0ac\uc6a9\uc81c\ud55c \ube44\uace0', blank=True)),
                ('license_number', models.CharField(unique=True, max_length=100, verbose_name='\uc790\uaca9\uc99d\ubc88\ud638')),
                ('car_number', models.CharField(unique=True, max_length=20, verbose_name='\ucc28\ub7c9\ubc88\ud638')),
                ('car_model', models.CharField(max_length=50, verbose_name='\ucc28\ub7c9\ubaa8\ub378')),
                ('company', models.CharField(max_length=50, verbose_name='\ud68c\uc0ac')),
                ('max_capacity', models.PositiveIntegerField(default=4, verbose_name='\ud0d1\uc2b9\uc778\uc6d0\uc218')),
                ('garage', models.CharField(max_length=100, verbose_name='\ucc28\uace0\uc9c0', blank=True)),
                ('taxi_type', models.CharField(max_length=10, verbose_name='\ud0dd\uc2dc\uc885\ub958', choices=[(b'private', '\uac1c\uc778'), (b'luxury', '\ubaa8\ubc94')])),
                ('taxi_service', cabbie.common.fields.SeparatedField(help_text='\ucf64\ub9c8(,)\ub85c \uad6c\ubd84\ud558\uc5ec \uc5ec\ub7ec \uac1c\uc758 \uc11c\ube44\uc2a4\ub97c \uc785\ub825\ud560 \uc218 \uc788\uc2b5\ub2c8\ub2e4.', separator=b',', max_length=1000, verbose_name='\uc11c\ube44\uc2a4', blank=True)),
                ('about', models.CharField(max_length=140, verbose_name='\uc18c\uac1c', blank=True)),
                ('deposit', models.IntegerField(default=0, verbose_name='\uc608\uce58\uae08')),
                ('is_super', models.BooleanField(default=False, verbose_name='\uc6b0\uc218\uae30\uc0ac')),
                ('is_dormant', models.BooleanField(default=False, verbose_name='\ud734\uba74\uae30\uc0ac')),
                ('total_ratings_by_category', cabbie.common.fields.JSONField(default=b'{}', verbose_name='\ucd1d\uc0c1\uc138\ud3c9\uc810')),
                ('user_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': '\uae30\uc0ac',
                'verbose_name_plural': '\uae30\uc0ac',
            },
            bases=('account.user', models.Model),
        ),
        migrations.CreateModel(
            name='DriverReservation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('image', models.ImageField(height_field=b'image_height', width_field=b'image_width', null=True, upload_to=cabbie.common.models._upload_to, blank=True)),
                ('image_key', models.CharField(max_length=100, blank=True)),
                ('image_width', models.IntegerField(null=True, blank=True)),
                ('image_height', models.IntegerField(null=True, blank=True)),
                ('phone', models.CharField(unique=True, max_length=11, verbose_name='\uc804\ud654\ubc88\ud638', validators=[cabbie.utils.validator.PhoneValidator()])),
                ('name', models.CharField(max_length=30, verbose_name='\uc774\ub984')),
                ('is_joined', models.BooleanField(default=False, verbose_name='\uac00\uc785\uc5ec\ubd80')),
            ],
            options={
                'verbose_name': '\uae30\uc0ac \uac00\uc785\uc2e0\uccad\uc790',
                'verbose_name_plural': '\uae30\uc0ac \uac00\uc785\uc2e0\uccad\uc790',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Dropout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('user_id', models.PositiveIntegerField()),
                ('note', models.CharField(max_length=1000, verbose_name='\ube44\uace0', blank=True)),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='DriverDropout',
            fields=[
                ('dropout_type', models.CharField(max_length=10, verbose_name='\ud0c8\ud1f4\uc0ac\uc720', choices=[(b'admin', '\uc6b4\uc601\uc790 \uc218\ub3d9'), (b'request', '\ud0c8\ud1f4 \uc694\uccad')])),
                ('dropout_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='account.Dropout')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uae30\uc0ac \ud0c8\ud1f4\uc790',
                'verbose_name_plural': '\uae30\uc0ac \ud0c8\ud1f4\uc790',
            },
            bases=('account.dropout',),
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('email', models.EmailField(unique=True, max_length=75, verbose_name='\uc774\uba54\uc77c')),
                ('user_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': '\uc2b9\uac1d',
                'verbose_name_plural': '\uc2b9\uac1d',
            },
            bases=('account.user',),
        ),
        migrations.CreateModel(
            name='PassengerDropout',
            fields=[
                ('dropout_type', models.CharField(max_length=10, verbose_name='\ud0c8\ud1f4\uc0ac\uc720', choices=[(b'admin', '\uc6b4\uc601\uc790 \uc218\ub3d9'), (b'request', '\ud0c8\ud1f4 \uc694\uccad')])),
                ('dropout_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to='account.Dropout')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc2b9\uac1d \ud0c8\ud1f4\uc790',
                'verbose_name_plural': '\uc2b9\uac1d \ud0c8\ud1f4\uc790',
            },
            bases=('account.dropout',),
        ),
    ]
