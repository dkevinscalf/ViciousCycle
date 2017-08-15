import tkinter as tk
import time
import CyclingRoutine
import CyclingActivity
import json
import datetime
import math

from enum import Enum
from pprint import pprint
from tkinter import *
from pygame import mixer

class FullScreenApp(object):
    def __init__(self, master, **kwargs):
        self.master=master
        pad=3
        self._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
        master.bind('<Escape>',self.toggle_geom)            
    def toggle_geom(self,event):
        geom=self.master.winfo_geometry()
        print(geom,self._geom)
        self.master.geometry(self._geom)
        self._geom=geom

#Global Vars
startTime = datetime.datetime.now()
deltaTime = 0
seconds = 0
remainingDuration = 0

#pulse vars
pulseOffTimer = 0
pulseOnTimer = 0
pulseOnCooldown = 10
currentRPM = 0

#Read Activity From File
segmentList = []

with open('SlowMobius.rtn') as data_file:    
    r = CyclingRoutine.RoutinePayload(data_file)

for segment in r.Segments:
    newSegment = CyclingRoutine.CSegment()
    newSegment.globalStartTime = segment['GlobalStartTime']
    newSegment.name = segment['Name']
    newSegment.events = []
    for event in segment['Events']:
        newEvent = CyclingRoutine.CEvent()
        newEvent.time = event['Time']
        newEvent.actionType = CyclingRoutine.ConvertIntToEventType(event['ActionType'])
        newEvent.actionParams = event['ActionParams']
        newSegment.events.append(newEvent)
    segmentList.append(newSegment)    

#Main Time Loop
def counter_label(label):
  def count():
    global deltaTime, seconds, remainingDuration, eventList

    deltaTime = datetime.datetime.now() - startTime

    #pulseRPM(deltaTime.seconds)

    seconds = int(deltaTime.seconds)

    displayDuration = remainingDuration - seconds

    label.config(text=getTime(seconds))
    durationLabel.config(text=getTime(displayDuration))
    
    eventControl(seconds)

    label.after(30, count)
  count()

def eventControl(seconds):
    global segmentList
    for cSegment in segmentList:
        if seconds>= cSegment.globalStartTime:
            for cEvent in cSegment.events:
                if seconds - cSegment.globalStartTime >= cEvent.time and cEvent.fired != True:
                    doAction(cEvent, cSegment.name)

def doAction(event, title):
    global mixer
    showTitle(title)
    if event.actionType == CyclingRoutine.CEventType.ACTIVITY:
        setActivity(event.actionParams)
    if event.actionType == CyclingRoutine.CEventType.MUSIC:
        playMusic(event.actionParams)
    if event.actionType == CyclingRoutine.CEventType.IMAGE:
        showImage(event.actionParams)
    if event.actionType == CyclingRoutine.CEventType.TEXT:
        showText(event.actionParams)
    event.fired = True

def setActivity(params):
    global remainingDuration, seconds, rpmLabel, wattLabel, standLabel, currentRPM
    activity = CyclingActivity.GetActivityFromActionParams(params)
    rpmLabel.config(text=activity.RPM)
    currentRPM = activity.RPM
    wattLabel.config(text=activity.WattRate)
    setColor(int(activity.WattRate))
    if activity.Stand == "True":
        standLabel.config(text="STAND")
    else:
        standLabel.config(text="SIT")
    remainingDuration = int(activity.Duration) + seconds

def setColor(wattRate):
    global rpmLabel, rpmImg, rpmImgL, wattLabel, wattImg, wattImgL, standLabel, standImg, standImgL, timer, timerImg, timerImgL, durationLabel, nextImg, nextImgL, titleLabel, contentText
    color = 'White'
    tColor = 'Black'
    if wattRate > 50:
        color = 'Blue'
        tColor = 'White'
    if wattRate > 65:
        color = 'Green'
        tColor = 'White'
    if wattRate > 80:
        color = 'Yellow'
        tColor = 'Black'
    if wattRate > 95:
        color = 'Red'
        tColor = 'White'
    root.config(background=color)
    titleLabel.config(background=color)
    titleLabel.config(fg=tColor)
    contentText.config(background=color)
    contentText.config(fg=tColor)
    rpmLabel.config(background=color)
    rpmLabel.config(fg=tColor)
    wattLabel.config(background=color)
    wattLabel.config(fg=tColor)
    standLabel.config(background=color)
    standLabel.config(fg=tColor)
    timer.config(background=color)
    timer.config(fg=tColor)
    durationLabel.config(background=color)
    durationLabel.config(fg=tColor)
    if tColor == 'Black':
        rpmLabel.config(image=rpmImg)
        wattLabel.config(image=wattImg)
        standLabel.config(image=standImg)
        timer.config(image=timerImg)
        durationLabel.config(image=nextImg)
    else:
        rpmLabel.config(image=rpmImgL)
        wattLabel.config(image=wattImgL)
        standLabel.config(image=standImgL)
        timer.config(image=timerImgL)
        durationLabel.config(image=nextImgL)

def playMusic(path):
    global mixer
    mixer.music.load(path)
    mixer.music.play()

def showImage(path):
    global contentLabel, contentImg
    contentImg = PhotoImage(file=path)
    contentLabel.config(image=contentImg)

def showTitle(title):
    global titleLabel
    titleLabel.config(text=title)

def showText(displayText):
    global contentText
    contentText.config(text=displayText)

def getTime(seconds):
    minutes = seconds // 60
    hours = minutes // 60   
    dSeconds = seconds % 60 
    dMinutes = minutes % 60
    if hours > 0:
        return str(hours) + ":" + str(dMinutes).zfill(2) + ":" + str(dSeconds).zfill(2)
    else:
        return str(dMinutes).zfill(2) + ":" + str(dSeconds).zfill(2)

def getMetricLabel(iconImage):
    return tk.Label(root, image=iconImage, compound = BOTTOM, fg='White', bg='Blue', font = "Helvetica 48 bold", padx = 20, pady = 20, relief = RAISED, anchor = N, bd=5)

def pulseRPM(deltaTime):
    global currentRPM, pulseOffTimer, pulseOnTimer, pulseOnCooldown, rpmLabel, pulseOffImg, pulseOnImg
    rpmVal = int(currentRPM)
    if rpmVal == 0:
        return
    period = 60 / rpmVal
    print(deltaTime)
    print(pulseOffTimer)
    if deltaTime > pulseOffTimer:
        pulseOffTimer = pulseOffTimer + period
        pulseOnTimer = deltaTime + 0.2
    if deltaTime > pulseOnTimer:
        rpmLabel.config(bd=15)
    else:
        rpmLabel.config(bd=5)

root=tk.Tk()
app=FullScreenApp(root)

root.configure(background="blue")

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
root.grid_columnconfigure(2, weight=1)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(4, weight=1)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=1)
root.grid_rowconfigure(2, weight=1)
root.grid_rowconfigure(3, weight=3)

mixer.init()

titleLabel = tk.Label(root, fg='White', bg='Blue', font = "Helvetica 48 bold", padx = 20, pady = 20)
titleLabel.grid(column=0, columnspan=3, row=0)

timerImg = PhotoImage(file="images/TTD.gif")
timerImgL = PhotoImage(file="images/TTL.gif")
timer = getMetricLabel(timerImg)
timer.grid(column=0, row=1, sticky=W+E)

rpmImg = PhotoImage(file="images/RPMD.gif")
rpmImgL = PhotoImage(file="images/RPML.gif")
rpmLabel = getMetricLabel(rpmImg)
rpmLabel.grid(column=1, row=1, sticky=W+E)

wattImg = PhotoImage(file="images/WD.gif")
wattImgL = PhotoImage(file="images/WL.gif")
wattLabel = getMetricLabel(wattImg)
wattLabel.grid(column=2, row=1, sticky=W+E)

standImg = PhotoImage(file="images/PD.gif")
standImgL = PhotoImage(file="images/PL.gif")
standLabel = getMetricLabel(standImg)
standLabel.grid(column=3, row=1, sticky=W+E)

nextImg = PhotoImage(file="images/ND.gif")
nextImgL = PhotoImage(file="images/NL.gif")
durationLabel = getMetricLabel(nextImg)
durationLabel.grid(column=4, row=1, sticky=W+E)

contentImg = PhotoImage(file="images/RM1.gif")
contentLabel = tk.Label(root, compound = CENTER)
contentLabel.grid(column=1, columnspan=3, row=3)

contentText = tk.Label(root, fg='White', bg='Blue', font = "Helvetica 30 bold", padx = 20, pady = 20)
contentText.grid(column=2, columnspan=3, row=2)

counter_label(timer)


root.mainloop()