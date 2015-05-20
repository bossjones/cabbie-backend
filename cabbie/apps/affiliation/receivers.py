# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import timezone

from cabbie.apps.affiliation.models import Affiliation
from cabbie.common.signals import post_create
from cabbie.utils.rand import random_string


def on_post_create_affiliation(sender, instance, **kwargs):
    # generate & update certificate code
    code = '{code}{date:%m%d}'.format(code=instance.company_code.upper(), date=instance.affiliated_at)

    instance.certificate_code = code
    instance.save(update_fields=['certificate_code'])

post_create.connect(on_post_create_affiliation, sender=Affiliation,
                    dispatch_uid='from_affiliation')
