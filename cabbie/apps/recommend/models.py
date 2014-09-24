# encoding: utf8

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from cabbie.common.models import AbstractTimestampModel


class Recommend(AbstractTimestampModel):
    PASSENGER_TO_PASSENGER, DRIVER_TO_DRIVER, DRIVER_TO_PASSENGER = (
        'p2p', 'd2d', 'd2p')

    RECOMMEND_TYPES = (
        (PASSENGER_TO_PASSENGER, u'승객 to 승객'),
        (DRIVER_TO_DRIVER, u'기사 to 기사'),
        (DRIVER_TO_PASSENGER, u'기사 to 승객'),
    )

    recommender_content_type = models.ForeignKey(
        ContentType, related_name='recommends_recommender')
    recommender_object_id = models.PositiveIntegerField()
    recommender = GenericForeignKey('recommender_content_type',
                                    'recommender_object_id')

    recommendee_content_type = models.ForeignKey(
        ContentType, related_name='recommends_recommendee')
    recommendee_object_id = models.PositiveIntegerField()
    recommendee = GenericForeignKey('recommendee_content_type',
                                    'recommendee_object_id')
    recommend_type = models.CharField(max_length=100, db_index=True,
                                      choices=RECOMMEND_TYPES)

    class Meta(AbstractTimestampModel.Meta):
        verbose_name = u'추천'
        verbose_name_plural = u'추천'
