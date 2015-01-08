# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='drivercoupon',
            options={'ordering': [b'-created_at'], 'verbose_name': '\uae30\uc0ac \ub9ac\uc6cc\ub4dc', 'verbose_name_plural': '\uae30\uc0ac \ub9ac\uc6cc\ub4dc'},
        ),
        migrations.AddField(
            model_name='drivercoupon',
            name='coupon_name',
            field=models.CharField(max_length=100, null=True, verbose_name='\ub9ac\uc6cc\ub4dc\uba85', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='drivercoupon',
            name='coupon_type',
            field=models.CharField(default=b'cash', max_length=100, verbose_name='\ub9ac\uc6cc\ub4dc \uc885\ub958', db_index=True, choices=[(b'cash', '\ud604\uae08'), (b'giftcard', '\uc0c1\ud488\uad8c')]),
        ),
    ]
