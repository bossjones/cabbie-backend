# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('drive', '0010_auto_20150821_1459'),
        ('education', '0001_initial'),
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProxyNotification',
            fields=[
            ],
            options={
                'verbose_name': '\uae30\uc0acSMS\uc54c\ub9bc',
                'proxy': True,
                'verbose_name_plural': '\uae30\uc0acSMS\uc54c\ub9bc',
            },
            bases=('notification.notification',),
        ),
        migrations.AlterModelOptions(
            name='notification',
            options={'ordering': ['-created_at'], 'verbose_name': '\uc2b9\uac1d\uc54c\ub9bc', 'verbose_name_plural': '\uc2b9\uac1d\uc54c\ub9bc'},
        ),
        migrations.AddField(
            model_name='notification',
            name='education',
            field=models.ForeignKey(related_name='notifications', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uad50\uc721\ucc28\uc218', blank=True, to='education.Education', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='is_freezed',
            field=models.NullBooleanField(verbose_name='\uc0ac\uc6a9\uc81c\ud55c'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='province',
            field=models.ForeignKey(related_name='notifications', on_delete=django.db.models.deletion.SET_NULL, verbose_name='\uc2dc\ub3c4', blank=True, to='drive.Province', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notification',
            name='region',
            field=models.CharField(max_length=20, null=True, verbose_name='\uc9c0\uc5ed', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='drivers',
            field=models.ManyToManyField(related_name='notifications', verbose_name='\ub300\uc0c1 \uae30\uc0ac', through='notification.NotificationDriverThrough', to='account.Driver'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='notification_type',
            field=models.CharField(default=b'sms', max_length=100, verbose_name='\uc54c\ub9bc \ud615\ud0dc', choices=[(b'sms', 'SMS'), (b'email', '\uc774\uba54\uc77c')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='notification',
            name='passengers',
            field=models.ManyToManyField(related_name='notifications', verbose_name='\ub300\uc0c1 \uc2b9\uac1d', through='notification.NotificationPassengerThrough', to='account.Passenger'),
            preserve_default=True,
        ),
    ]
