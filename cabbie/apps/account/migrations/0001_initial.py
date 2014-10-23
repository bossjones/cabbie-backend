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
                ('phone', models.CharField(unique=True, max_length=11, verbose_name='phone', validators=[cabbie.utils.validator.PhoneValidator()])),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('is_staff', models.BooleanField(default=False, verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('point', models.PositiveIntegerField(default=0)),
                ('recommend_code', models.CharField(default=cabbie.apps.account.models._issue_new_code, unique=True, max_length=10)),
                ('is_bot', models.BooleanField(default=False)),
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
                ('verification_code', models.CharField(max_length=10)),
                ('is_verified', models.BooleanField(default=False)),
                ('is_accepted', models.BooleanField(default=False)),
                ('is_freezed', models.BooleanField(default=False)),
                ('license_number', models.CharField(unique=True, max_length=100, verbose_name='license number')),
                ('car_number', models.CharField(unique=True, max_length=20, verbose_name='car number')),
                ('car_model', models.CharField(max_length=50, verbose_name='car model')),
                ('company', models.CharField(max_length=50, verbose_name='company')),
                ('bank_account', models.CharField(max_length=100, verbose_name='bank account')),
                ('max_capacity', models.PositiveIntegerField(default=4, verbose_name='max capacity')),
                ('taxi_type', models.CharField(max_length=10, choices=[(b'private', '\uac1c\uc778'), (b'luxury', '\ubaa8\ubc94')])),
                ('taxi_service', cabbie.common.fields.SeparatedField(max_length=1000, separator=b',', blank=True)),
                ('about', models.CharField(max_length=140, blank=True)),
                ('total_rating', models.PositiveIntegerField(default=0, verbose_name='total rating')),
                ('rated_count', models.PositiveIntegerField(default=0, verbose_name='rated count')),
                ('ride_count', models.PositiveIntegerField(default=0, verbose_name='ride count')),
                ('deposit', models.IntegerField(default=0, verbose_name='deposit')),
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
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, editable=False, db_index=True)),
                ('phone', models.CharField(unique=True, max_length=11, verbose_name='phone', validators=[cabbie.utils.validator.PhoneValidator()])),
                ('name', models.CharField(max_length=30, verbose_name='name')),
                ('is_joined', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': '\uae30\uc0ac \uac00\uc785\uc2e0\uccad\uc790',
                'verbose_name_plural': '\uae30\uc0ac \uac00\uc785\uc2e0\uccad\uc790',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Passenger',
            fields=[
                ('email', models.EmailField(unique=True, max_length=75, verbose_name='email address')),
                ('ride_count', models.PositiveIntegerField(default=0, verbose_name='ride count')),
                ('user_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
                'verbose_name': '\uc2b9\uac1d',
                'verbose_name_plural': '\uc2b9\uac1d',
            },
            bases=('account.user',),
        ),
    ]
