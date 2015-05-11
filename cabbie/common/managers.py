import datetime

from django.utils import timezone

class TimezoneManager(object):
    def astimezone(self, field):
        qs = self.get_queryset()
        for q in qs:
            value = getattr(q, field, None)
            if value and isinstance(value, datetime.datetime) and value.tzinfo:
                value = timezone.get_current_timezone().normalize(value)
                setattr(q, field, value)
        return qs
                
    
