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
            name='Notification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uc0dd\uc131\uc2dc\uac04', editable=False, db_index=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='\uac31\uc2e0\uc2dc\uac04', editable=False, db_index=True)),
                ('notification_type', models.CharField(max_length=100, verbose_name='\uc54c\ub9bc \ud615\ud0dc', choices=[(b'sms', 'SMS'), (b'email', '\uc774\uba54\uc77c')])),
                ('body', models.TextField(verbose_name='\uc54c\ub9bc \ub0b4\uc6a9')),
                ('is_all_passengers', models.BooleanField(default=False, help_text='\uac1c\ubcc4 \uc9c0\uc815\ud558\uc9c0 \ud558\uace0 \ubaa8\ub4e0 \uc2b9\uac1d\uc5d0\uac8c \uc804\uc1a1\ud560 \uacbd\uc6b0 \uc120\ud0dd\ud569\ub2c8\ub2e4', verbose_name='\ubaa8\ub4e0 \uc2b9\uac1d \ub300\uc0c1')),
                ('is_all_drivers', models.BooleanField(default=False, help_text='\uac1c\ubcc4 \uc9c0\uc815\ud558\uc9c0 \ud558\uace0 \ubaa8\ub4e0 \uae30\uc0ac\uc5d0\uac8c \uc804\uc1a1\ud560 \uacbd\uc6b0 \uc120\ud0dd\ud569\ub2c8\ub2e4', verbose_name='\ubaa8\ub4e0 \uae30\uc0ac \ub300\uc0c1')),
                ('notified_passenger_count', models.PositiveIntegerField(default=0, verbose_name='\ucd1d \uc804\uc1a1 (\uc2b9\uac1d)')),
                ('notified_driver_count', models.PositiveIntegerField(default=0, verbose_name='\ucd1d \uc804\uc1a1 (\uae30\uc0ac)')),
            ],
            options={
                'ordering': [b'-created_at'],
                'abstract': False,
                'verbose_name': '\uc54c\ub9bc',
                'verbose_name_plural': '\uc54c\ub9bc',
            },
            bases=(cabbie.common.models.JSONMixin, cabbie.common.models.UpdateMixin, models.Model),
        ),
        migrations.CreateModel(
            name='NotificationDriverThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('driver', models.ForeignKey(verbose_name='\uae30\uc0ac', to='account.Driver')),
            ],
            options={
                'verbose_name': '\ub300\uc0c1 \uae30\uc0ac',
                'verbose_name_plural': '\ub300\uc0c1 \uae30\uc0ac',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='notification',
            name='drivers',
            field=models.ManyToManyField(to='account.Driver', verbose_name='\ub300\uc0c1 \uae30\uc0ac', through='notification.NotificationDriverThrough'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationdriverthrough',
            name='notification',
            field=models.ForeignKey(verbose_name='\uc54c\ub9bc', to='notification.Notification'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='NotificationPassengerThrough',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'verbose_name': '\ub300\uc0c1 \uc2b9\uac1d',
                'verbose_name_plural': '\ub300\uc0c1 \uc2b9\uac1d',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='notification',
            name='passengers',
            field=models.ManyToManyField(to='account.Passenger', verbose_name='\ub300\uc0c1 \uc2b9\uac1d', through='notification.NotificationPassengerThrough'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationpassengerthrough',
            name='notification',
            field=models.ForeignKey(verbose_name='\uc54c\ub9bc', to='notification.Notification'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notificationpassengerthrough',
            name='passenger',
            field=models.ForeignKey(verbose_name='\uc2b9\uac1d', to='account.Passenger'),
            preserve_default=True,
        ),
    ]
