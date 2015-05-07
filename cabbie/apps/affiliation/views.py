from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from cabbie.common.views import APIMixin, APIView
from cabbie.apps.affiliation.serializers import AffiliationSerializer
from cabbie.apps.account.serializers import PassengerSerializer
from cabbie.apps.affiliation.models import Affiliation

ERR_001 = ('affiliation code does not exists',              'affiliation.E001')
ERR_002 = ('this affiliation is not active',                'affiliation.E002')
ERR_003 = ('param "certificate_code" is required',          'affiliation.E003')

class AffiliationViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer
    
    ordering = ('-created_at',)

class CheckAffiliationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        code = request.QUERY_PARAMS.get('certificate_code')

        if code:
            try:
                code = code.upper()
                affiliation = Affiliation.objects.get(certificate_code=code)

            except Affiliation.DoesNotExist as e:
                return self.render_error(*ERR_001)

            if not affiliation.is_active:
                return self.render_error(*ERR_002)

            return self.render()

        return self.render_error(*ERR_003)

class RegisterAffiliationView(APIView):
    def post(self, request, *args, **kwargs):
        user = request.user.concrete

        code = request.DATA.get('certificate_code')       
 
        if code:
            try:
                code = code.upper()
                affiliation = Affiliation.objects.get(certificate_code=code)

            except Affiliation.DoesNotExist as e:
                return self.render_error(*ERR_001)

            if not affiliation.is_active:
                return self.render_error(*ERR_002)

            user.affiliation = affiliation
            user.save(update_fields=['affiliation'])
        
            return self.render(PassengerSerializer(user).data)

        return self.render_error(*ERR_003)
