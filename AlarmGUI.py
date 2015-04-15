from Tkinter import *

class AlarmView:
    def __init__(self, root, settings, parent):
        self.root = root
        self.parent = parent
        self.settings = settings
        self.initialize()

    def initialize(self):     
        self.rightFrame = Frame(self.root, width = 72 , height = 202)

        self.bLights = Button(self.rightFrame, text="Lights", command = self.parent.lights)
        self.bLights.grid(row = 0, pady = 2)
        self.bSleep = Button(self.rightFrame, text="Sleep", command = self.parent.sleep)
        self.bSleep.grid(row = 1, pady = 2)
        self.lTempCurr = Label(self.rightFrame, text="")
        self.lTempCurr.grid(row = 2)
        self.lTempHigh = Label(self.rightFrame, text="")
        self.lTempHigh.grid(row = 3)
        self.lTempLow = Label(self.rightFrame, text="")
        self.lTempLow.grid(row = 4)
        self.lPrecip = Label(self.rightFrame, text="")
        self.lPrecip.grid(row = 5)
        Label(self.rightFrame, text="").grid(row = 6, pady = 6)
        self.bAlarmSettings = Button(self.rightFrame, text="Settings", command = self.alarmSettings)
        self.bAlarmSettings.grid(row = 7)
        
        self.leftFrame = Frame(self.root, width = 70)
        
        self.lLeftFrame = Label(self.leftFrame, text="Events")
        self.lLeftFrame.grid(row = 0)
        self.lEvent1 = Label(self.leftFrame, text="")
        self.lEvent1.grid(row = 1)
        self.lEvent2 = Label(self.leftFrame, text="")
        self.lEvent2.grid(row = 2)
        self.lEvent3 = Label(self.leftFrame, text="")
        self.lEvent3.grid(row = 3)

        
        self.lAlarm = Label(self.root, text='')
        self.lAlarm.place(x=5, y=205)
        
        self.lTime = Label(self.root, text="", font=('Helvetica', 40))
        
        self.leftFrame.pack(side=LEFT, anchor='nw', padx = 5, pady = 20)
        self.lTime.pack(side=LEFT, expand = 'true')
        self.rightFrame.pack(side=LEFT, anchor='e', padx = 5, pady = 18)
        
    def alarmSettings(self):
        self.toplevel = Toplevel()
        self.toplevel.title('Settings')
        self.toplevel.geometry('+10+10')
        self.toplevel.focus()
        
        self.lDefaultAlarm = Label(self.toplevel, text='Default Alarm:')
        self.lDefaultAlarm.grid(row = 0)
        defaultHour = StringVar(self.toplevel)
        defaultHour.set(self.settings.defaultAlarm[:2])
        defaultMinute = StringVar(self.toplevel)
        defaultMinute.set(self.settings.defaultAlarm[3:])
        self.sDefaultHour = Spinbox(self.toplevel, from_= 00, to=12, wrap = True, width = 10, textvariable = defaultHour)
        self.sDefaultHour.grid(row = 0, column = 1)
        self.sDefaultMinute = Spinbox(self.toplevel, from_= 00, to=59, wrap = True, width = 10, textvariable = defaultMinute)
        self.sDefaultMinute.grid(row = 0, column = 2)

        self.lDefaultSound = Label(self.toplevel, text='Default Sound File:')
        self.lDefaultSound.grid(row = 1, columnspan = 3)
        defaultSound = StringVar(self.toplevel)
        defaultSound.set(self.settings.alarmSound)
        self.eDefaultSound = Entry(self.toplevel, width = 30, textvariable = defaultSound)
        self.eDefaultSound.grid(row = 2, columnspan = 3)
        
        self.lDefaultAlarm = Label(self.toplevel, text='Your Zipcode:')
        self.lDefaultAlarm.grid(row = 3)
        defaultZipCode = StringVar(self.toplevel)
        defaultZipCode.set(self.settings.zipCode)
        self.eDefaultZipCode = Entry(self.toplevel, textvariable = defaultZipCode)
        self.eDefaultZipCode.grid(row = 3, column = 1, columnspan = 2)
        
        self.bDaylight = Button(self.toplevel, text="Daylight", command=lambda: self.parent.setLightColor('DAYLIGHT'))
        self.bDaylight.grid(row = 4)
        self.bEvening = Button(self.toplevel, text="Red Light", command=lambda: self.parent.setLightColor('SUNSET_RED'))
        self.bEvening.grid(row = 4, column = 1)
        self.bMorning = Button(self.toplevel, text="Blue Light", command=lambda: self.parent.setLightColor('MORNING_BLUE'))
        self.bMorning.grid(row = 4, column = 2)
        self.bSave = Button(self.toplevel, text='Save Settings', command = self.parent.saveSettings)
        self.bSave.grid(row = 5, column = 2)
        
    def setLabel(self, key, label):
        self.labels[key].configure(text=label)