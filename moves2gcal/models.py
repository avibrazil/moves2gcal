from __future__ import unicode_literals

#import requests
import json
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
		  "globals": {
			"mergeSamePlacesWithWalks": 1,
			"defaultTarget": "Moves Test"
		  },
		  "rules": [
			{
			  "type": "normal",
			  "target": "nameOneCalendar",
			  "places": [
				{
				  "name": "humanName",
				  "4sqid": "id"
				},
				{
				  "name": "humanName",
				  "4sqid": "id"
				}
			  ]
			},
			{
			  "type": "normal",
			  "target": "nameTwoCalendar",
			  "places": [
				{
				  "name": "humanName",
				  "4sqid": "id"
				},
				{
				  "name": "humanName",
				  "4sqid": "id"
				}
			  ]
			},
			{
			  "type": "ignore",
			  "places": [
				{
				  "name": "humanName",
				  "4sqid": "id"
				},
				{
				  "name": "humanName",
				  "4sqid": "id"
				}
			  ]
			},
		  ]
		}
    """
    
    def compilePrefs(self):
        self.preferences=json.loads(self.calendarprefs)

    def calendarForPlace(self, name=None, foursquareId=None):
    	for ignoreOrNormal in ('ignore', 'normal'):
			for searchFor in ('4sqid', 'name'):
				for r in self.preferences['rules']:
					for p in r['places']:
						if searchFor == '4sqid':
							if foursquareId == p['4sqid']:
								if r['type'] == 'ignore':
									return None
								else:
									return r['target']
						else:
							if name == p['name']:
								if r['type'] == 'ignore':
									return None
								else:
									return r['target']
		
    	return self.preferences.globals['defaultTarget']
    
    
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user.username