from __future__ import unicode_literals

#import requests
from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user               = models.ForeignKey(User, db_index=True)
    movesstart         = models.DateField(verbose_name='First date on Moves', null=True, default=None)
    lastplacesync      = models.DateTimeField(verbose_name='Date of last place pulled to GCal', null=True, default=None)
    calendarprefs      = models.TextField(null=True, default=None)
    
    """
    calendarprefs should have this data architecture:
    
    {
    	"rules": [
    		{
				"targetCalendar": CALENDAR_NAME
				"places": [
					PLACE_NAME_1,
					PLACE_NAME_2,
					PLACE_NAME_3
				]
    		},
    		{
				"targetCalendar": CALENDAR_NAME
				"places": [
					PLACE_NAME_1,
					PLACE_NAME_2,
					PLACE_NAME_3
				]
    		}
    	],
    	"defaultTargetCalendar": CALENDAR_NAME
    }
    """
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user.username