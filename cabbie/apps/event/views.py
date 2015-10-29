# encoding: utf-8

from rest_framework.permissions import AllowAny

from cabbie.common.views import APIView
from cabbie.apps.account.models import PassengerDropout
from cabbie.apps.event.models import CuEventCode, EVENT_CU

# Error message
# -------------
ERR_001 = ('parameter "phone", "promotion_code" should be provided',   'event.E001')
ERR_002 = ('there exists dropout history',   'event.E002')
ERR_003 = ('code is not valid',   'event.E003')

class EventCodeCheckView(APIView):
    permission_classes = (AllowAny,) 

    def get(self, request, *args, **kwargs):
        phone = request.GET.get('phone')
        promotion_code = request.GET.get('promotion_code')

        # param check
        if phone is None or promotion_code is None:
            return self.render_error(*ERR_001)
        
        # CU
        # --

        # dropout history check 
        dropouts = PassengerDropout.objects.all()

        for dropout in dropouts:
            note = dropout.note
    
            if note:
                dropout_name, dropout_phone = note.split() 

                if phone == dropout_phone:
                    return self.render_error(*ERR_002)

        # code validation check
        try:
            CuEventCode.objects.get(code=promotion_code)
        except CuEventCode.DoesNotExist, e:
            return self.render_error(*ERR_003)

        promotion_type = EVENT_CU
        
        # To be filled, future vendors come here ...

        return self.render({
            'promotion_type': promotion_type
        })

