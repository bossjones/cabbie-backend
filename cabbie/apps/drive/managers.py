from django.db import models

from cabbie.common.managers import TimezoneManager as BaseTimezoneManager

class TimezoneManager(BaseTimezoneManager, models.Manager):
    def __init__(self, *args, **kwargs):
        super(TimezoneManager, self).__init__(*args, **kwargs) 
    
