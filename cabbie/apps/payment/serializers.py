from cabbie.apps.drive.serializers import RideSerializer
from cabbie.apps.payment.models import Transaction, DriverBill, DriverCoupon
from cabbie.apps.recommend.serializers import RecommendSerializer
from cabbie.common.serializers import AbstractSerializer


class TransactionSerializer(AbstractSerializer):
    ride = RideSerializer(read_only=True)
    recommend = RecommendSerializer(read_only=True)

    class Meta:
        model = Transaction
        fields = ('id', 'ride', 'recommend', 'transaction_type', 'amount',
                  'note', 'created_at')

class DriverBillSerializer(AbstractSerializer):
    class Meta:
        model = DriverBill
        fields = ('id', 'amount', 'created_at')

class DriverCouponSerializer(AbstractSerializer):
    class Meta:
        model = DriverCoupon
        fields = ('id', 'coupon_type', 'coupon_name', 'amount', 'created_at', 
                  'is_processed', 'processed_at')       

    
 
