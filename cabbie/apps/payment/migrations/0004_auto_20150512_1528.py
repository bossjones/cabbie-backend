# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0003_auto_20150306_1544'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverreturn',
            name='is_requested',
            field=models.BooleanField(default=False, verbose_name='\ud658\uae09\uc694\uccad\uc815\ubcf4 \uae30\uc785\uc5ec\ubd80'),
        ),
        migrations.AlterField(
            model_name='passengerreturn',
            name='is_requested',
            field=models.BooleanField(default=False, verbose_name='\ud658\uae09\uc694\uccad\uc815\ubcf4 \uae30\uc785\uc5ec\ubd80'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='recommend',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ucd94\ucc9c', blank=True, to='recommend.Recommend', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='ride',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, verbose_name='\ucf5c', blank=True, to='drive.Ride', null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='transaction_type',
            field=models.CharField(db_index=True, max_length=100, verbose_name='\uc885\ub958', choices=[(b'signup_point', '\uc2e0\uaddc\uac00\uc785 \ud3ec\uc778\ud2b8'), (b'ride_point', '\ud0d1\uc2b9 \ud3ec\uc778\ud2b8'), (b'rate_point', '\ud3c9\uac00 \ud3ec\uc778\ud2b8'), (b'recommend', '\ucd94\ucc9c'), (b'recommended', '\ud53c\ucd94\ucc9c'), (b'grant', '\uc9c0\uae09'), (b'return', '\ud658\uae09')]),
        ),
    ]
