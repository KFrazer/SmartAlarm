import time
import os
import pywapi
from Tkinter import *
import httplib2
import sys
import argparse
import datetime
from datetime import time, timedelta
import time
import logging
from lazylights import *
from threading import Timer
#import RPi.GPIO as GPIO
#import wiringpi

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import tools
from oauth2client.tools import run_flow

import AlarmModel

class APIMethods:
    def __init__(self, client_id, client_secret):
        self.settings = AlarmModel.Settings()
        #dimmer = ?18?
        #wiringpi.wiringPiSetup()
        #wiringpi.pinMode(dimmer, 2) #Just to note- dimmer is the pin number for BCM 18. Not sure what to number that here.
        
        # Arguments for flow, from Google API
        scope = 'https://www.googleapis.com/auth/calendar'
        redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'

        # Create a flow object. This object holds the client_id, client_secret, and
        # scope. It assists with OAuth 2.0 steps to get user authorization and
        # credentials.
        self.flow = OAuth2WebServerFlow(client_id, client_secret, scope, redirect_uri, user_agent = 'SmartAlarm/0.9')
        self.flags = tools.argparser.parse_args(args=[])
        logging.basicConfig()

    def C2F(self, celsius):
        return (9.0/5.0 * int(celsius) + 32)

    def pullCalendar(self):
        # Create a Storage object. This object holds the credentials that your
        # application needs to authorize access to the user's data.
        storage = Storage('credentials.dat')
        credentials = storage.get()

        # If we don't already have the credentials, get them.
        if credentials is None or credentials.invalid:
            credentials = run_flow(self.flow, storage, self.flags)

        # Create an httplib2.Http object to handle our HTTP requests, and authorize it
        # using the credentials.authorize() function.
        http = httplib2.Http()
        http = credentials.authorize(http)

        # The apiclient.discovery.build() function returns an instance of an API service
        # object can be used to make API calls. The object is constructed with
        # methods specific to the calendar API. The arguments provided are:
        #   name of the API ('calendar')
        #   version of the API you are using ('v3')
        #   authorized httplib2.Http() object that can be used for API calls
        service = build('calendar', 'v3', http=http)

        # get the next 24 hours of events
        epoch_time = time.time()
        start_time = epoch_time # now
        end_time = epoch_time + 24 * 3600  # 12 hours in the future
        tz_offset = - time.altzone / 3600 # tz is clearly timezone offset
        if tz_offset < 0:
            tz_offset_str = "-%02d00" % abs(tz_offset)
        else:
            tz_offset_str = "+%02d00" % abs(tz_offset)

        start_time = datetime.datetime.fromtimestamp(start_time).strftime("%Y-%m-%dT%H:%M:%S") + tz_offset_str
        end_time = datetime.datetime.fromtimestamp(end_time).strftime("%Y-%m-%dT%H:%M:%S") + tz_offset_str

        try:
            # Loop until all pages have been processed.
            request = service.events().list(calendarId='primary', timeMin=start_time, timeMax = end_time, singleEvents=True).execute()
            eventTimes = []
            for event in request['items']:
                if 'dateTime' in event['start']:
                    eventTimes.append(event)

            eventTimes.sort(key=lambda event: event['start']['dateTime'])
            previousEvent = ''
            events = []
            for event in eventTimes:
                s = event['start']['dateTime']
                eventString = s[5:7] + '/' + s[8:10] + ' ' + s[11:16]
                if eventString != previousEvent:
                    events.append(eventString)
                    previousEvent = eventString
                
            return events

        except AccessTokenRefreshError:
            # The AccessTokenRefreshError exception is raised if the credentials
            # have been revoked by the user or they have expired.
            print 'The credentials have been revoked or expired, please re-run the application to re-authorize'


    def pullWeather(self):
        weather_com_result = pywapi.get_weather_from_weather_com(self.settings.zipCode)
        current_temp = str(round(self.C2F(weather_com_result["current_conditions"]["temperature"]), 1))
        high_temp = str(round(self.C2F(weather_com_result["forecasts"][0]["high"]), 1))
        low_temp = str(round(self.C2F(weather_com_result["forecasts"][0]["low"]), 1))
        precip = str(weather_com_result["forecasts"][0]["day"]["chance_precip"])
        text = str(weather_com_result["current_conditions"]["text"])

        return {'current_temp':current_temp, 'high_temp':high_temp, 'low_temp':low_temp, 'precip':precip, 'text':text}
        
    # There is some funky string slicing happening here to compare all these different strings. I have to pull out
    # the different parts of the date.
    def setAlarm(self, events, raining):
        alarm = self.settings.defaultAlarm
        alarmSet = False
        
        dt = datetime.datetime.now()
        today = dt.strftime('%m/%d')
        t = dt + timedelta(days=1)
        tomorrow = t.strftime('%m/%d')
        
        # I believe event[0:5] is the date, event[6:] is hour and minutes, event[6:8] is the hour, and event[9:] is the minutes.
        # The string alarm[:2] is the hour and alarm[3:] is the minutes.
        # I'm converting string representations of times into dates here so that I can compare them.
        if dt.hour < 14:
            for event in events:
                if event[0:5] == today and datetime.time(int(event[6:8]) - 1, int(event[9:])) <= datetime.time(int(alarm[0:2]), int(alarm[3:])):
                    alarm = event[6:]
                    alarmSet = True
        else:
            for event in events:
                if event[0:5] == tomorrow and datetime.time(int(event[6:8]), int(event[9:])) <= datetime.time(int(alarm[0:2]), int(alarm[3:])):
                    alarm = event[6:]
                    alarmSet = True

        if alarmSet:
            if raining:
                adjustedTime = datetime.datetime(2000, 1, 1, int(alarm[0:2]), int(alarm[3:]), 00) - timedelta(hours=1, minutes=30)
            else:
                adjustedTime = datetime.datetime(2000, 1, 1, int(alarm[0:2]), int(alarm[3:]), 00) - timedelta(hours=1)
            alarm = adjustedTime.strftime('%H:%M')
        
        sleepTime = datetime.datetime(2000, 1, 1, int(alarm[0:2]), int(alarm[3:]), 00) - timedelta(hours=8)
        sleep = sleepTime.strftime('%H:%M')
        
        return alarm, sleep

    def saveSettings(self):
        defaultHour = self.sDefaultHour.get()
        defaultMinute = self.sDefaultMinute.get()
        if not len(defaultHour) > 1:
            defaultHour = '0' + defaultHour
        if not len(defaultMinute) > 1:
            defaultMinute = '0' + defaultMinute
        self.settings.defaultAlarm = defaultHour + ':' + defaultMinute
        self.settings.alarmSound = self.eDefaultSound.get()
        self.settings.zipCode = self.eDefaultZipCode.get()
        self.settings.save()
                
#We are creating a process that can sit in a while loop watching for keyboard interrupts and looping the song
'''  
    def toggleScreen(self):
        wiringpi.pwmWrite(dimmer,0) #Off
        wiringpi.pwmWrite(dimmer,255) #On
'''    
    
'''        
    def setNixieTime(self, time):
        PIN_DATA=23
        PIN_LATCH=24
        PIN_CLK=25
        
        try:
            nixie = Nixie(PIN_DATA, PIN_LATCH, PIN_CLK, 4)
            
            nixie.set_value(int(time[:2])*100 + int(time[3:]))

        finally:
            # Cleanup GPIO on exit. Otherwise, you'll get a warning next time toy
            # configure the pins.
            GPIO.cleanup()

class Nixie:
    def __init__(self, pin_data, pin_latch, pin_clk, digits):
        self.pin_data = pin_data
        self.pin_latch = pin_latch
        self.pin_clk = pin_clk
        self.digits = digits

        GPIO.setmode(GPIO.BCM)

        # Setup the GPIO pins as outputs
        GPIO.setup(self.pin_data, GPIO.OUT)
        GPIO.setup(self.pin_latch, GPIO.OUT)
        GPIO.setup(self.pin_clk, GPIO.OUT)

        # Set the initial state of our GPIO pins to 0
        GPIO.output(self.pin_data, False)
        GPIO.output(self.pin_latch, False)
        GPIO.output(self.pin_clk, False)

    def delay(self):
        # We'll use a 10ms delay for our clock
        time.sleep(0.010)

    def transfer_latch(self):
        # Trigger the latch pin from 0->1. This causes the value that we've
        # been shifting into the register to be copied to the output.
        GPIO.output(self.pin_latch, True)
        self.delay()
        GPIO.output(self.pin_latch, False)
        self.delay()

    def tick_clock(self):
        # Tick the clock pin. This will cause the register to shift its
        # internal value left one position and the copy the state of the DATA
        # pin into the lowest bit.
        GPIO.output(self.pin_clk, True)
        self.delay()
        GPIO.output(self.pin_clk, False)
        self.delay()

    def shift_bit(self, value):
        # Shift one bit into the register.
        GPIO.output(self.pin_data, value)
        self.tick_clock()

    def shift_digit(self, value):
        # Shift a 4-bit BCD-encoded value into the register, MSB-first.
        self.shift_bit(value&0x08)
        value = value << 1
        self.shift_bit(value&0x08)
        value = value << 1
        self.shift_bit(value&0x08)
        value = value << 1
        self.shift_bit(value&0x08)

    def set_value(self, value):
        # Shift a decimal value into the register

        str = "%0*d" % (self.digits, value)

        for digit in str:
            self.shift_digit(int(digit))
            value = value * 10

        self.transfer_latch()
'''
