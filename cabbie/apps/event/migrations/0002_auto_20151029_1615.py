# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CuEventCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=10, verbose_name='\ucf54\ub4dc')),
            ],
            options={
                'verbose_name': 'CU \uc774\ubca4\ud2b8\ucf54\ub4dc',
                'verbose_name_plural': 'CU \uc774\ubca4\ud2b8\ucf54\ub4dc',
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='ridepointevent',
            name='is_accomplished',
            field=models.BooleanField(default=False, verbose_name='\ub2ec\uc131\uc5ec\ubd80 (\uc120\ucc29\uc21c\uc77c \ub54c\ub9cc \uc801\uc6a9)'),
            preserve_default=True,
        ),
    ]
