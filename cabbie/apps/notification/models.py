# encoding: utf8

from django.db import models

from cabbie.apps.account.models import Passenger, Driver
from cabbie.apps.drive.models import Province
from cabbie.apps.education.models import Education
from cabbie.common.models import AbstractTimestampModel


class Notification(AbstractTimestampModel):
    SMS, EMAIL = 'sms', 'email'
    NOTIFICATION_TYPES = (
        (SMS, u'SMS'),
        (EMAIL, u'이메일'),
    )

    passengers = models.ManyToManyField(Passenger,
                                        related_name='notifications',
                                        verbose_name=u'대상 승객',
                                        through='NotificationPassengerThrough')
    drivers = models.ManyToManyField(Driver, related_name='notifications',
                                     verbose_name=u'대상 기사',
                                     through='NotificationDriverThrough')
    notification_type = models.CharField(u'알림 형태', max_length=100,
                                         choices=NOTIFICATION_TYPES, default=SMS)
    body = models.TextField(u'알림 내용')
    is_all_passengers = models.BooleanField(
        u'모든 승객 대상', default=False,
        help_text=u'개별 지정하지 하고 모든 승객에게 전송할 경우 선택합니다')
    is_all_drivers = models.BooleanField(
        u'모든 기사 대상', default=False,
        help_text=u'개별 지정하지 하고 모든 기사에게 전송할 경우 선택합니다')
    notified_passenger_count = models.PositiveIntegerField(u'총 전송 (승객)',
                                                           default=0)
    notified_driver_count = models.PositiveIntegerField(u'총 전송 (기사)',
                                                        default=0)

    is_test = models.BooleanField(u'테스트', default=True)

    # only for drivers
    is_freezed = models.BooleanField(u'사용제한자 대상', default=False)
    education = models.ForeignKey(Education, related_name='notifications', verbose_name=u'교육차수', blank=True, null=True, on_delete=models.SET_NULL)
    is_educated = models.NullBooleanField(u'교육이수여부')
    province = models.ForeignKey(Province, related_name='notifications', verbose_name=u'시도', blank=True, null=True, on_delete=models.SET_NULL)
    region = models.CharField(u'지역', max_length=20, blank=True, null=True)
 
    
    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'승객알림'
        verbose_name_plural = u'승객알림'


class NotificationPassengerThrough(models.Model):
    passenger = models.ForeignKey(Passenger, verbose_name=u'승객')
    notification = models.ForeignKey(Notification, verbose_name=u'알림')

    class Meta:
        verbose_name = u'대상 승객'
        verbose_name_plural = u'대상 승객'


class NotificationDriverThrough(models.Model):
    driver = models.ForeignKey(Driver, verbose_name=u'기사')
    notification = models.ForeignKey(Notification, verbose_name=u'알림')

    class Meta:
        verbose_name = u'대상 기사'
        verbose_name_plural = u'대상 기사'


from cabbie.apps.notification.receivers import *
