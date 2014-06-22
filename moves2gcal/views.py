from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib import messages
from social.apps.django_app.default.models import UserSocialAuth
from social.utils import url_add_parameters
from dateutil import parser
import requests
import json

class Place:
    # def __init__(self,
            # name, start, end, lat, lon, obj=None):
        # self.name=name
        # self.start=parser.parse(start)
        # self.end=parser.parse(end)
        # self.map='https://www.google.com/maps/@{0},{1},15z'.format(lat,lon)
        # self.movesObject=obj

    def __init__(self,mplace=None):
        self.movesObject = mplace
        self.type = mplace['place']['type']
        self.start = parser.parse(mplace['startTime'])
        self.end   = parser.parse(mplace['endTime'])
        self.map   = 'https://www.google.com/maps/@{0},{1},15z'.format(
            mplace['place']['location']['lat'],
            mplace['place']['location']['lon'])

        if 'name' in mplace['place']:
            self.location = mplace['place']['name']
        else:
            self.location = 'Unknown'
        
        # Parse activities
        if 'activities' in mplace:
            atxt=''
            for a in mplace['activities']:
                if a['manual'] == False and \
                        'group' in a and \
                        a['group'] == 'walking':
                    # skip if its autodetected plain walking activity
                    continue
                    
                if atxt != '':
                    atxt += u" \u2022 "
                    
                if 'distance' in a:
                    dis = int(a['distance'])
                    if dis > 1000:
                        dis = "{0}km".format(dis/1000)
                    else:
                        dis = "{0}m".format(dis)
                else:
                    dis = ''
                
                if 'duration' in a:
                    d = int(a['duration'])
                    dur = ''
                    if d >= 3600:
                        dur = "{0}h".format(d/3600)
                    if d >= 60:
                        dur += "{0}m".format((d%3600)/60)
                    dur += "{0}s".format(((d%3600)%60)/60)
                else:
                    dur=''
                    
                atxt += "{what} {duration} {distance}".format(
                    what=a['activity'].capitalize().replace('_',' '),
                    duration=dur,
                    distance=dis
                )
                
            # Remove extra white space (http://stackoverflow.com/a/4241775)
            self.activity=' '.join(atxt.split())
        else:
            self.activity = ''
        
        # Fill with details
        self.details = ''
        self.details += 'On the map: https://www.google.com/maps/@{0},{1},15\n'.format(
            mplace['place']['location']['lat'],
            mplace['place']['location']['lon'])
            
        if self.type == 'foursquare':
            self.details += 'On Foursquare: https://foursquare.com/v//{0}\n'.format(
            mplace['place']['foursquareId'])
            
        self.details += 'Moves\' place ID: {0}'.format(mplace['place']['id'])
        
        

    def gcalJSON(self):
        template='{\
          "kind": "calendar#event",\
          "id": "string",\
          "summary": "{summary}",\
          "description": "{details}",\
          "location": "{location}",\
          "start": {\
            "dateTime": "{startDateTime}",\
          },\
          "end": {\
            "dateTime": "{endDateTime}",\
          },\
          "source": {\
            "url": "http://homeavi.alkalay.net:8081/",\
            "title": "Moves app Places to Google Calendar"\
          }\
        }'
        
        return template.format(
            summary = self.activity,
            location = self.location,
            details = self.details,
            startDateTime = self.start.isoformat(),
            endDateTime = self.end.isoformat(),
        )


class GoogleCalendars:
    def __init__(self, user,
            api_url = 'https://www.googleapis.com/calendar/v3',
            agent_name = 'Moves app to Google Calendar'):
        self.user = user
        self.api_url = api_url
        self.apikey = {} # not necessary when useing OAuth
        self.apiheaders = {
            'Authorization': '{0} {1}'.format(
                self.user.extra_data['token_type'],
                self.user.extra_data['access_token']),
             'User-Agent': agent_name
        }
        
        self.cal = {}
        self.lasterror = ''
        
        self.get_calendars()
    
    
    def get_calendars(self):
        root = '/users/me/calendarList'
        
        response=requests.get(self.api_url + root,
            params = self.apikey,
            headers = self.apiheaders)
            
        self.log='{0}<br/>{1}'.format(response.request.url,
            response.request.headers)
        
        jresponse=response.json()
        
        if 'items' in jresponse:
            self.lasterror = ''
            for cal in jresponse['items']:
                if cal['accessRole'] != 'freeBusyReader' and cal['accessRole'] != 'reader':
                    c = {
                        'name': cal['summary'],
                        'colors': [
                            cal['backgroundColor'],
                            cal['foregroundColor']
                        ]
                    }

                    if 'primary' in cal and cal['primary'] == 'true':
                        self.cal['primary'] = c
                    else:
                        self.cal[cal['id']] = c
        elif 'error' in jresponse:
            self.lasterror = '{0} {1}'.format(
                jresponse['error']['code'],
                jresponse['error']['message']
            )


class Moves:
    def __init__(self, user,
            api_url = 'https://api.moves-app.com/api/1.1'):
        self.api_url = api_url
        self.user = user

    # /user/profile
    def get_profile(self):
        root = '/user/profile'
        
        uri=url_add_parameters(self.api_url + root, {
            'access_token': self.user.extra_data['access_token']
        })
        
        return requests.get(uri).json()
#        return uri

    def get_places_activities(self):
        root = '/user/storyline/daily'
        
        i=0
        places=[]
        
        uri=url_add_parameters(self.api_url + root, {
            'access_token': self.user.extra_data['access_token'],
            'trackPoints': 'false',
            'from': self.user.extra_data['firstdate'],
            'to': '20140420'
        })
        
        storyline=requests.get(uri).json()
        
        for day in storyline:
            for mplace in day['segments']:
                if mplace['type'] == 'place':
                    p=None
                    p=Place(mplace)
                    places.append(p)

        return places


# Class to hold all context to run stuff: Moves ID, Google ID etc
"""
class Moves2GCal:
    def initMovesFromAuthorizationCode(self,authorization_code):
        try:
            self.m=Moves.objects.get(authorization_code=authorization_code)
            self.m.set_client_info(client_id,client_secret)
        except ObjectDoesNotExist:
            # New user (doesn't exist on DB). Retrieve other tokens from Moves web service.
            self.m=Moves()
            self.m.set_client_info(client_id,client_secret)
            self.m.negotiate_tokens(authorization_code)

"""

def home(request):
    if request.user.is_authenticated():
        try:
            movesuser=UserSocialAuth.objects.get(user=request.user, provider='moves')
            moves=Moves(movesuser)
            p=moves.get_places_activities()
        except ObjectDoesNotExist:
            movesuser=UserSocialAuth
            p=''
        try:
            googleuser=UserSocialAuth.objects.get(user=request.user, provider='google-oauth2')
            gcal=GoogleCalendars(googleuser)
            c=gcal.cal
#            messages.info(request, 'Google Calendar: {0}'.format(gcal.log))
            if gcal.lasterror:
                messages.warning(request, 'Google Calendar: {0}'.format(gcal.lasterror))
        except ObjectDoesNotExist:
            googleuser=UserSocialAuth
            c=''
            
    else:
        movesuser=UserSocialAuth
        googleuser=UserSocialAuth
        p=''
        c=''
    
#    m2g=Moves2GCal()

    context = RequestContext(request, {
        'user': request.user,
        'moves': movesuser,
        'google': googleuser,
        'places': p
#        'moves': m2g.m,
    })
    return render_to_response('moves2gcal/index.html',context_instance=context)
