from __future__ import unicode_literals

#import requests
from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user               = models.ForeignKey(User, db_index=True)
    movesstart         = models.DateField(verbose_name='First date on Moves', null=True, default=None)
    lastplacesync      = models.DateTimeField(verbose_name='Date of last place pulled to GCal', null=True, default=None)
    calendarprefs      = models.TextField(null=True, default=None)
    
    
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user.username