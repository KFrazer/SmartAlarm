#!/usr/bin/python
import json
import os.path

global programDefaults
programDefaults = {}
programDefaults['defaultAlarm'] = '11:00'
programDefaults['raining'] = 'False'
programDefaults['zipCode'] = '30318'
programDefaults['alarmSound'] = 'NatureSounds.mp3'
programDefaults['sleepTimer'] = 60 * 5

class Settings:
    def __init__(self):
        global programDefaults
        if os.path.isfile('AlarmSettings.json'):
            with open('AlarmSettings.json', 'r') as infile:
                settings = json.load(infile)
        else:
            settings = programDefaults

        self.defaultAlarm = settings['defaultAlarm']
        self.zipCode = settings['zipCode']
        if settings['raining'] == 'True':
            self.raining = True
        else:
            self.raining = False
        self.alarmSound = settings['alarmSound']
        self.sleepTimer = settings['sleepTimer']
        
        self.save()
    
    def save(self):
        settings = {}
        settings['defaultAlarm'] = self.defaultAlarm
        settings['zipCode'] = self.zipCode
        if self.raining:
            settings['raining'] = 'True'
        else:
            settings['raining'] = 'False'
        settings['alarmSound'] = self.alarmSound
        settings['sleepTimer'] = self.sleepTimer

        with open('AlarmSettings.json', 'w') as outfile:
            json.dump(settings, outfile)

        
        