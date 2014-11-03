from import_export import resources, fields

from cabbie.apps.payment.models import (
    PassengerReturn, DriverReturn)


class AbstractReturnResource(resources.ModelResource):
    pass


class PassengerReturnResource(AbstractReturnResource):
    phone = fields.Field(attribute='phone')
    bank_account = fields.Field(attribute='bank_account')

    class Meta:
        model = PassengerReturn


class DriverReturnResource(AbstractReturnResource):
    phone = fields.Field(attribute='phone')
    bank_account = fields.Field(attribute='bank_account')

    class Meta:
        model = DriverReturn
