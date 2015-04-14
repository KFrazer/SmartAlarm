#!/usr/bin/python
# -*- coding: iso-8859-1 -*-

import Tkinter
from Tkinter import Label, Button, Frame
import time
import sys
import AlarmAPI
import AlarmGUI
import AlarmModel
from lazylights import *
from subprocess import Popen, PIPE
from threading import Timer

class SmartAlarm(Tkinter.Tk):
    def __init__(self, root):
        Tkinter.Tk.__init__(self, root)
        self.root = root
        self.settings = AlarmModel.Settings()
        self.API = AlarmAPI.APIMethods()
        self.view = AlarmGUI.AlarmView(root, self.settings, self)

        self.alarmOn = False
        self.sleepOn = False

        self.bulbs = find_bulbs(expected_bulbs=1)
        self.SUNSET_RED = ('SUNSET_RED', 0, 0.20, 0.95, 2000) #in HSV
        self.MORNING_BLUE = ('MORNING_BLUE', 210, 0.20, 0.90, 2000) #in HSV
        self.DAYLIGHT = ('DAYLIGHT', 0, 0, 1, 4500) #in Kelvin
        self.COLORS = [self.SUNSET_RED, self.MORNING_BLUE, self.DAYLIGHT]
        self.setLightColor('DAYLIGHT')
        
        self.initialize()
        #self.overrideredirect(True) #Gets rid of title bar

    def initialize(self):  
        self.updateCalendar()
        self.updateWeather()
        alarmTuple = self.API.setAlarm(self.events, self.raining)
        self.alarm = alarmTuple[0]
        self.sleep = alarmTuple[1]
        self.view.lAlarm.configure(text="Alarm Set For: " + str(self.alarm))
    
        self.currTime = ''
        self.GUITimer()
        
    def GUITimer(self):
        # get the current local time from the PC
        newTime = time.strftime("%H:%M")
        # if currTime string has changed, update it
        if newTime != self.currTime:
            if '00' == newTime[3:]:
                self.updateCalendar()
                self.updateWeather()
                alarmTuple = self.API.setAlarm(self.events, self.raining)
                self.alarm = alarmTuple[0]
                self.sleep = alarmTuple[1]
                self.view.lAlarm.configure(text="Alarm Set For: " + str(self.alarm))
            if newTime == self.alarm:
                self.API.soundAlarm(self)
            if newTime == self.sleep:
                self.API.setLightColor('SUNSET_RED')
            
            self.currTime = newTime
            self.view.lTime.configure(text=self.currTime)
        
        if self.alarmOn is True and self.sound is not None and self.sound.poll() is not None:
                self.sound = Popen(['omxplayer', 'WakeMeUp.ogg'], stdin=PIPE)
        
        #calls itself after 5 seconds
        self.after(5000, self.GUITimer)
    
    def updateCalendar(self):
        self.events = self.API.pullCalendar()

        i = 0
        for event in self.events:
            if i == 0:
                self.view.lEvent1.configure(text=event)
                i += 1
            elif i == 1:
                self.view.lEvent2.configure(text=event)
                i += 1
            elif i == 2:
                self.view.lEvent3.configure(text=event)

    def updateWeather(self):
        try:
            weather = self.API.pullWeather()
            self.view.lTempCurr.config(text = ('Temp: ' + weather["current_temp"] + 'F'))
            self.view.lTempHigh.config(text = ('Hi: ' + weather["high_temp"] + 'F'))
            self.view.lTempLow.config(text = ('Lo: ' + weather["low_temp"] + 'F'))
            self.view.lPrecip.config(text = ('Precip: ' + weather["precip"] + '%'))
            
            if int(weather["precip"]) > 70:
                self.raining = True
            else:
                self.raining = False
            
        except:
            self.raining = False 
            
    def soundAlarm(self):
        self.alarmOn = True
        if self.sleepOn:
            self.sleepOn = False
        self.setLightColor('MORNING_BLUE')
        if self.sound is not None:
            self.sound.communicate('q')
            self.sound.terminate()
        self.sound = Popen(['omxplayer', self.settings.alarmSound], stdin=PIPE)
    
    def sleep(self):
        if self.alarmOn:
            self.alarmOn = False
            set_power(self.bulbs, False)
            self.bulbs_power = False
            self.sleepOn = True
            self.sound.communicate('q')
            self.sound.terminate()
            self.sleepCallback = Timer(self.settings.sleepTimer, self.soundAlarm)
            self.sleepCallback.start()
        else:
            self.soundAlarm()
            
    def lights(self):
        if self.alarmOn:
            self.alarmOn = False
            self.sound.communicate('q')
            self.sound.terminate()
        elif self.bulbs_power:
            set_power(self.bulbs, False)
            self.bulbs_power = False
        else:
            if self.sleepOn:
                self.setLightColor('MORNING_BLUE')
                self.sleepCallback.cancel()
                self.sleepOn = False
            else:
                self.setLightColor('DAYLIGHT')

    def setLightColor(self, color):
        set_power(self.bulbs, True)
        self.bulbs_power = True
        
        lColor = self.COLORS[2]
        for item in [item for item in self.COLORS if item[0] == color]:
            lColor = item

        set_state(self.bulbs, lColor[1], lColor[2], lColor[3], lColor[4], 0, raw=False)
        self.bulbs_color = lColor[0]
            
    def resetBulbs(self):
        self.bulbs = find_bulbs(expected_bulbs=1)
        
    def saveSettings(self):
        defaultHour = self.view.sDefaultHour.get()
        defaultMinute = self.view.sDefaultMinute.get()
        if not len(defaultHour) > 1:
            defaultHour = '0' + defaultHour
        if not len(defaultMinute) > 1:
            defaultMinute = '0' + defaultMinute
        self.settings.defaultAlarm = defaultHour + ':' + defaultMinute
        self.settings.alarmSound = self.view.eDefaultSound.get()
        self.settings.zipCode = self.view.eDefaultZipCode.get()
        self.settings.save()
            
if __name__ == "__main__":
    white = '#%02x%02x%02x' % (255, 255, 255)
    app = SmartAlarm(None)
    app.title('Alarm')
    app.configure(bg = white)
    app.tk_setPalette(background=white)
    app.geometry("320x240+0+0")
    app.mainloop()