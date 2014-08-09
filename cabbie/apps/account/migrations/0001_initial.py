# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
from django.conf import settings
import cabbie.utils.validator


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
                ('groups', models.ManyToManyField(to='auth.Group', verbose_name='groups', blank=True)),
                ('user_permissions', models.ManyToManyField(to='auth.Permission', verbose_name='user permissions', blank=True)),
            ],
            options={
                'ordering': [b'-date_joined'],
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Driver',
            fields=[
                ('licence_number', models.CharField(unique=True, max_length=100, verbose_name='license number')),
                ('ride_count', models.PositiveIntegerField(default=0, verbose_name='ride count')),
                ('user_ptr', models.OneToOneField(auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('account.user',),
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
            },
            bases=('account.user',),
        ),
    ]
