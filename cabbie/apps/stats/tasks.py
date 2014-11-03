from celery.task import Task
from django.conf import settings

from cabbie.apps.account.models import Driver


class CouponMonthlyTask(Task):
    def run(self, *args, **kwargs):
        for driver in Driver.objects.filter(is_accepted=True,
                                            is_freezed=False):

            for threshold, amount in settings.COUPON_THRESHOLDS:
                if driver.previous_month_board_count >= threshold:
                    driver.coupons.create(amount=amount)
                    break
