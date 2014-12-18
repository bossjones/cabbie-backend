# encoding: utf8

import random
import string

from cabbie.apps.account.models import Passenger, Driver, User
from cabbie.utils.log import LoggableMixin
from cabbie.utils.meta import SingletonMixin
from cabbie.utils.rand import weighted_choice, weighted_boolean, random_string
from cabbie.utils import json


class BotFactory(LoggableMixin, SingletonMixin):
    @staticmethod
    def random_zfill_int(size):
        return unicode(random.randint(0, 10 ** size - 1)).zfill(size)

    def create(self, count=1):
        self.info('Creating {0} bot(s)'.format(count))

        for i in range(count):
            self.create_bot()

    def create_bot(self):
        raise NotImplementedError

    def _generate_phone(self, driver):
        while True:
            phone = u'010{0}'.format(self.random_zfill_int(8))
            if not User.objects.filter(phone=phone).exists():
                return phone

    def _generate_name(self, driver):
        return random.choice([u'{0}로봇'.format(c) for c in (
            u'정', u'김', u'이', u'차', u'홍', u'김', u'박', u'최', u'강',
            u'조', u'윤', u'장', u'임',
        )])


class DriverBotFactory(BotFactory):
    fields_to_generate = (
        'phone',
        'name',
        'license_number',
        'car_number',
        'car_model',
        'company',
        'bank_account',
        'max_capacity',
        'taxi_type',
        'taxi_service',
        'about',
    )

    def create_bot(self):
        driver = Driver()

        driver.is_bot = True
        driver.is_verified = True
        driver.is_accepted = True

        for field in self.fields_to_generate:
            method = getattr(self, '_generate_{field}'.format(field=field))
            setattr(driver, field, method(driver))

        driver.save()

        return driver

    def _generate_license_number(self, driver):
        while True:
            value = u'서울 {0}-{1}-{2}'.format(
                self.random_zfill_int(2),
                self.random_zfill_int(6),
                self.random_zfill_int(2),
            )
            if not Driver.objects.filter(license_number=value).exists():
                return value

    def _generate_car_number(self, driver):
        while True:
            value = u'{0}봇 {1}'.format(
                self.random_zfill_int(2),
                self.random_zfill_int(4),
            )
            if not Driver.objects.filter(car_number=value).exists():
                return value

    def _generate_car_model(self, driver):
        return random.choice([
            u'SONATA EF',
            u'SONATA NF',
            u'SONATA YF',
            u'SONATA LF',
            u'GRANDEUR XG',
            u'GRANDEUR TG',
            u'K5',
            u'SM5',
        ])

    def _generate_company(self, driver):
        return random.choice([u'로봇회사{0}'.format(c)
                              for c in string.ascii_uppercase])

    def _generate_bank_account(self, driver):
        return u'{0} {1}-{2}-{3}'.format(
            random.choice([
                u'국민은행',
                u'우리은행',
                u'하나은행',
                u'농협',
                u'외환은행',
                u'기업은행',
            ]),
            self.random_zfill_int(6),
            self.random_zfill_int(2),
            self.random_zfill_int(6),
        )

    def _generate_max_capacity(self, driver):
        return random.randint(2, 4)

    def _generate_taxi_type(self, driver):
        return weighted_choice((
            (Driver.TAXI_PRIVATE, 4),
            (Driver.TAXI_LUXURY, 1),
        ))

    def _generate_taxi_service(self, driver):
        service = []

        if weighted_boolean(1, 2):
            service.append(u'안드로이드')
        if weighted_boolean(1, 3):
            service.append(u'방향제')
        if weighted_boolean(1, 4):
            service.append(u'안심문자')
        if weighted_boolean(1, 5):
            service.append(u'네비게이션')

        return service

    def _generate_about(self, driver):
        mode = weighted_choice((
            ('blank', 4),
            ('one', 1),
            ('two', 1),
        ))
        if mode == 'blank':
            return u''
        elif mode == 'one':
            return u'저는 로봇택시입니다.'
        elif mode == 'two':
            return u'저는 로봇택시입니다.\n그렇지만 운행은 합니다.'


class PassengerBotFactory(BotFactory):
    fields_to_generate = (
        'phone',
        'name',
        'email',
    )

    def create_bot(self):
        passenger = Passenger()

        passenger.is_bot = True

        for field in self.fields_to_generate:
            method = getattr(self, '_generate_{field}'.format(field=field))
            setattr(passenger, field, method(passenger))

        passenger.save()

        return passenger

    def _generate_email(self, passenger):
        while True:
            email = u'{0}@bktaxi.com'.format(random_string(8))
            if not Passenger.objects.filter(email=email).exists():
                return email
