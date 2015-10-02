# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0015_driver_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='last_notice_checked_at',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='\ub9c8\uc9c0\ub9c9 \uacf5\uc9c0\uc0ac\ud56d \ud655\uc778\uc2dc\uac04'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driver',
            name='education',
            field=models.ForeignKey(related_name='attendees', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uad50\uc721', blank=True, to='education.Education', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driver',
            name='user_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='driverdropout',
            name='dropout_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='account.Dropout'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='passenger',
            name='affiliation',
            field=models.ForeignKey(related_name='passengers', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc81c\ud734\uc0ac', blank=True, to='affiliation.Affiliation', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='passenger',
            name='user_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='passengerdropout',
            name='dropout_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='account.Dropout'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions'),
            preserve_default=True,
        ),
    ]
