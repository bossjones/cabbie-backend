from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from cabbie.common.views import APIMixin, APIView
from cabbie.apps.affiliation.serializers import AffiliationSerializer
from cabbie.apps.affiliation.models import Affiliation

class AffiliationViewSet(APIMixin, viewsets.ModelViewSet):
    queryset = Affiliation.objects.all()
    serializer_class = AffiliationSerializer
    
    ordering = ('-created_at',)

class CheckAffiliationView(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        try:
            affiliation = Affiliation.objects.get(certificate_code=request.QUERY_PARAMS['certificate_code'])
        except Affiliation.DoesNotExist as e:
            return self.render_error(unicode(e))

        if not affiliation.is_active:
            return self.render_error('Not active affiliation company')

        return self.render({})
        
            
        
