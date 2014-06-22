from __future__ import unicode_literals

#import requests
from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user               = models.ForeignKey(User, db_index=True)
    movesstart         = models.DateField(verbose_name='First date on Moves', default='2014-03-28')
    lastplacesync      = models.DateTimeField(verbose_name='Date of last place pulled to GCal', default='2014-03-28 00:00:00')
    calendarprefs      = models.CharField(max_length=8000, null=True)
    
    
    
    def __unicode__(self):  # Python 3: def __str__(self):
        return self.user.username

