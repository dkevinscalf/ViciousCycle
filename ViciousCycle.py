import tkinter as tk
import time
import CyclingRoutine
import CyclingActivity
import CyclingRider
import json
import datetime
import math
import os

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
masterDeltaTime = 0
lastTickTime = datetime.datetime.now()
deltaTime = 0
seconds = 0
remainingDuration = 0

timeMultiplier = 1

colorWidgets = []
colorImages = []

#pulse vars
pulseOffTimer = 0
pulseOnTimer = 0
pulseOnCooldown = 10
currentRPM = 0

#race vars
racingTime = -10
racingWindow = None
racingFrame = None
racingLabel = None
racingTitleLabel = None
racingBars = []
racingWinner = None

leaderBoardFrame = None
rpmImgL = None
wattImgL = None



#Read Activity From File
segmentList = []

#Read Rider List From File
riderList = []
#riderList.append(CyclingRider.CRider('Kevin', 0, 0, 0, 125, "ec:27:71:d6:23:37"))
#riderList.append(CyclingRider.CRider('Wes', 0, 0, 0, 125, "d3:25:1a:26:8b:bd"))
#riderList.append(CyclingRider.CRider('Tim', 0, 0, 0, 125, "c0:2f:37:77:43:00"))
#riderList.append(CyclingRider.CRider('Drew', 0, 0, 0, 125, "f2:4f:e2:4e:51:64"))
#riderList.append(CyclingRider.CRider('Kevin', 0, 0, 0, 125, "d4:da:3c:9a:34:b8"))
#riderList.append(CyclingRider.CRider('Wes', 0, 0, 0, 125, "f1:9c:5e:00:b3:86"))
#riderList.append(CyclingRider.CRider('Tim', 0, 0, 0, 125, "f4:77:6b:ab:ff:ec"))
#riderList.append(CyclingRider.CRider('Drew', 0, 0, 0, 125, "c7:79:50:46:4c:21"))

with open('BikeConfig.txt', 'rt') as csvfile:
    for line in csvfile.readlines():
        line = line.replace("\n", "")
        if len(line) > 1:
            lineParts = line.split(',')
            print(lineParts)
            if lineParts[3] == "1":
                riderList.append(CyclingRider.CRider(lineParts[1], 0, 0, 0, int(lineParts[2]), lineParts[0]))
            

routineFile = sys.argv[1]

with open(routineFile) as data_file:    
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
    global masterDeltaTime, deltaTime, lastTickTime, seconds, remainingDuration, eventList, timeMultiplier, racingTime

    masterDeltaTime = datetime.datetime.now() - startTime
    deltaTime = datetime.datetime.now() - lastTickTime
    lastTickTime = datetime.datetime.now()

    #pulseRPM(masterDeltaTime.seconds)

    seconds = int(masterDeltaTime.seconds) * timeMultiplier

    updateLeaderBoard()

    for rider in riderList:
        rider.runOdometer(deltaTime.total_seconds())

    displayDuration = remainingDuration - seconds

    if racingTime > -5:
        runRace(deltaTime.total_seconds());
    elif racingWindow != None:
        racingWindow.destroy();

    label.config(text=getTime(seconds))
    durationLabel.config(text=getTime(displayDuration))
    
    eventControl(seconds)

    label.after(30, count)
  count()

def getRiderInput(leaderboardFrame):
  def simulateRiders():
    global riderList

    for rider in riderList:
        rider.Simulate()

    updateLeaderBoard()

    leaderboardFrame.after(500, simulateRiders)

  def readRiderData():
    global riderList

    with open('BikeData.txt', 'rt') as csvfile:
        for line in csvfile.readlines():
           if len(line) > 1:
               lineParts = line.split(',')
               bikeID = lineParts[0]
               for rider in riderList:
                   if rider.BikeID == bikeID:
                       rider.ParseFromBikeData(lineParts[1])

    updateLeaderBoard()

    leaderboardFrame.after(500, readRiderData)
  #simulateRiders()
  readRiderData()

def createRaceWindow():
    global racingWindow, racingFrame, racingLabel, racingBar, riderList, racingTitleLabel
    racingWindow = Toplevel()    
    racingFrame = tk.Frame(racingWindow, width=1200, height=600, bg='black')    
    racingFrame.pack()
    
    racingFrame.grid_columnconfigure(0, weight=1)
    racingFrame.grid_columnconfigure(1, weight=1)
    racingFrame.grid_rowconfigure(0, weight=1)
    racingTitleLabel = tk.Label(racingFrame, text="RACE", fg='White', bg='black', font = "Helvetica 36 bold")
    racingTitleLabel.grid(column=1, row=0, sticky="nsew")
    i = 1
    for rider in riderList:
        racingFrame.grid_rowconfigure(i, weight=1)
        racingLane = tk.Frame(racingFrame, width=1000, bg='black', padx=10, pady=10)
        racingLane.grid(column=1, row=i, sticky="nsew")
        racingBar = tk.Label(racingLane, bg="bisque", width=100, height=10)
        racingBar.pack(side= LEFT)
        racingBars.append(racingBar)
        racingRiderLabel = tk.Label(racingFrame, text=rider.RiderName, fg='White', bg='black', font = "Helvetica 36 bold")
        racingRiderLabel.grid(column=0, row=i, sticky="nsew")
        i = i + 1

def runRace(seconds):
    global racingTime, racingFrame, racingLabel, racingWindow, riderList, racingBars, racingTitleLabel, racingWinner
    if racingWindow == None:
        return
    racingTime-=seconds
    racingText = ""
    if racingTime < 1:
        if racingWinner == None:
            currentWinner = 0;
            for rider in riderList:
                if rider.PowerSecondsTrip > currentWinner:
                    currentWinner = rider.PowerSecondsTrip
                    racingWinner = "Finish! " + rider.RiderName + " Wins!"
                    print(racingWinner)
        racingTitleLabel.configure(text=racingWinner)
    if racingTime >= 0:
        i = 0
        racingTitleLabel.configure(text="RACE " + str(int(racingTime)))
        maxPowerTrip = getMaxPowerTrip(riderList)
        for rider in riderList:            
            racingBars[i].configure(width=int(rider.PowerSecondsTrip / maxPowerTrip * 100))
            i = i+1
    

def getMaxPowerTrip(riderList):
    powerTrip = 0
    for rider in riderList:
        if rider.PowerSecondsTrip > powerTrip:
            powerTrip = rider.PowerSecondsTrip
    return powerTrip

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
    if event.actionType == CyclingRoutine.CEventType.RACE:
        startRace(event.actionParams)
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
    global colorWidgets, colorImages, timerImg, rpmImg, wattImg, standImg, nextImg
    for widget in colorWidgets:
        widget.configure(bg=getBGColorByWattRate(wattRate))
        try:
          widget.configure(fg=getFGColorByWattRate(wattRate))
          widget.configure(image=getImageByWattRate(wattRate))
        except: 
          pass

    for imageWidget, darkImage, lightImage in colorImages:
        imageWidget.configure(image=getImageByWattRate(lightImage, darkImage, wattRate))

def getBGColorByWattRate(wattRate):
    color = 'White'
    if wattRate > 50:
        color = 'Blue'
    if wattRate > 65:
        color = 'Green'
    if wattRate > 80:
        color = 'Yellow'
    if wattRate > 95:
        color = 'Red'
    return color

def getFGColorByWattRate(wattRate):
    tColor = 'Black'
    if wattRate > 50:
        tColor = 'White'
    if wattRate > 65:
        tColor = 'White'
    if wattRate > 80:
        tColor = 'Black'
    if wattRate > 95:
        tColor = 'White'
    return tColor

def getImageByWattRate(lightImage, darkImage, wattRate):
    image = darkImage      
    if wattRate > 50:
        image = lightImage
    if wattRate > 65:
        image = lightImage
    if wattRate > 80:
        image = darkImage
    if wattRate > 95:
        image = lightImage
    return image

def playMusic(path):
    global mixer
    mixer.music.load(path)
    mixer.music.play()

def showImage(path):
    global contentLabel, contentImg
    contentImg = PhotoImage(file=path)
    contentLabel.config(image=contentImg)

def startRace(path):
    global racingTime
    createRaceWindow()
    racingTime = float(path)
    for rider in riderList:
        rider.PowerSecondsTrip = 0

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

def getMetricLabel(iconImage, parent):
    return tk.Label(parent, image=iconImage, compound = BOTTOM, fg='White', bg='Blue', font = "Helvetica 48 bold", padx = 20, pady = 20, relief = RAISED, anchor = N, bd=5)

def getRiderLabel(iconImage, parent):
    label = getMetricLabel(iconImage, parent)
    label.configure(font= "Helvetica 30 bold")
    return label

def pulseRPM(masterDeltaTime):
    global currentRPM, pulseOffTimer, pulseOnTimer, pulseOnCooldown, rpmLabel, pulseOffImg, pulseOnImg
    rpmVal = int(currentRPM)
    if rpmVal == 0:
        return
    period = 60 / rpmVal
    if masterDeltaTime > pulseOffTimer:
        pulseOffTimer = pulseOffTimer + period
        pulseOnTimer = masterDeltaTime + 0.2
    if masterDeltaTime > pulseOnTimer:
        rpmLabel.config(bd=15)
    else:
        rpmLabel.config(bd=5)

def createLeaderBoard():
    global riderList, leaderBoardFrame, rpmImgL, rpmImgD, wattImgL, wattImgD

    nameLabel = tk.Label(leaderBoardFrame, compound = BOTTOM, fg='White', bg='Blue', font = "Helvetica 24 bold", relief = RAISED, bd=2)
    nameLabel.grid(column=0, row=0, sticky="nsew")
    colorWidgets.append(nameLabel)
    rpmLabel = tk.Label(leaderBoardFrame, image=rpmImgL, compound = BOTTOM, fg='White', bg='Blue', font = "Helvetica 24 bold", relief = RAISED, bd=2)
    rpmLabel.grid(column=1, row=0, sticky="nsew")
    colorWidgets.append(rpmLabel)
    colorImages.append((rpmLabel, rpmImgD, rpmImgL))
    wattLabel = tk.Label(leaderBoardFrame, image=wattImgL, compound = BOTTOM, fg='White', bg='Blue', font = "Helvetica 24 bold", relief = RAISED, bd=2)
    wattLabel.grid(column=2, row=0, sticky="nsew")
    colorWidgets.append(wattLabel)
    colorImages.append((wattLabel, wattImgD, wattImgL))

    i=1
    for rider in riderList:
        nameLabel = tk.Label(leaderBoardFrame, fg='White', bg='Blue', font = "Helvetica 24 bold", relief = RAISED, bd=2, text=rider.RiderName)
        nameLabel.grid(column=0, row=i, sticky="nsew")
        rider.NameLabel = nameLabel
        rpmLabel = tk.Label(leaderBoardFrame, fg='White', bg='Blue', font = "Helvetica 24 bold", relief = RAISED, bd=2)
        rpmLabel.grid(column=1, row=i, sticky="nsew")
        rider.RPMLabel = rpmLabel
        wattLabel = tk.Label(leaderBoardFrame, fg='White', bg='Blue', font = "Helvetica 24 bold", relief = RAISED, bd=2)
        wattLabel.grid(column=2, row=i, sticky="nsew")
        rider.WattLabel = wattLabel
        i+=1

def updateLeaderBoard():
    global riderList
    for rider in riderList:
        rider.RPMLabel.configure(text=rider.RPM)
        rider.WattLabel.configure(text=rider.WattPercentage())
        rider.ColorLeaderBoard(getBGColorByWattRate(rider.WattPercentage()),getFGColorByWattRate(rider.WattPercentage()))

root=tk.Tk()
app=FullScreenApp(root)

root.configure(background="blue")

mixer.init()

topFrame = tk.Frame(bg="blue")
topFrame.pack(anchor=N, fill=X, expand=False)

titleFrame = tk.Frame(topFrame, bg="blue")
titleFrame.pack(fill=X, expand=True)

programFrame = tk.Frame(topFrame, bg="blue")
programFrame.pack(fill=BOTH, expand=True)

textFrame = tk.Frame(topFrame, bg="blue")
textFrame.pack(fill=X, expand=True)

bottomFrame = tk.Frame(bg="blue")
bottomFrame.pack(fill=BOTH, expand=True)
colorWidgets.append(bottomFrame)

leaderBoardFrame = tk.Frame(bottomFrame, bg="blue")
leaderBoardFrame.pack(fill=BOTH, expand=True, side=LEFT)

leaderBoardFrame.grid_columnconfigure(0, weight=1)
leaderBoardFrame.grid_columnconfigure(1, weight=1)
leaderBoardFrame.grid_columnconfigure(2, weight=1)

leaderBoardFrame.grid_rowconfigure(0, weight=1)
leaderBoardFrame.grid_rowconfigure(1, weight=1)
leaderBoardFrame.grid_rowconfigure(2, weight=1)
leaderBoardFrame.grid_rowconfigure(3, weight=1)
leaderBoardFrame.grid_rowconfigure(4, weight=1)
leaderBoardFrame.grid_rowconfigure(5, weight=1)
leaderBoardFrame.grid_rowconfigure(6, weight=1)
leaderBoardFrame.grid_rowconfigure(7, weight=1)
leaderBoardFrame.grid_rowconfigure(8, weight=1)
colorWidgets.append(leaderBoardFrame)

imageFrame = tk.Frame(bottomFrame, bg="black")
imageFrame.pack(fill=BOTH, expand=True, side=LEFT)
colorWidgets.append(imageFrame)

titleLabel = tk.Label(titleFrame, fg='White', bg='Blue', font = "Helvetica 48 bold", padx = 20, pady = 20, anchor = W, text='Test Layout')
titleLabel.pack(fill=BOTH, expand=True)
colorWidgets.append(titleLabel)

timerImgD = PhotoImage(file="images/TTD.gif")
timerImgL = PhotoImage(file="images/TTL.gif")
timerImg = timerImgL
timer = getMetricLabel(timerImgL, programFrame)
timer.pack(fill=BOTH, expand=True, side=LEFT)
timer.configure(text='00:00:00')
colorWidgets.append(timer)
colorImages.append((timer, timerImgD, timerImgL))

rpmImgD = PhotoImage(file="images/RPMD.gif")
rpmImgL = PhotoImage(file="images/RPML.gif")
rpmImg = rpmImgL
rpmLabel = getMetricLabel(rpmImgL, programFrame)
rpmLabel.pack(fill=BOTH, expand=True, side=LEFT)
rpmLabel.configure(text='0')
colorWidgets.append(rpmLabel)
colorImages.append((rpmLabel, rpmImgD, rpmImgL))

wattImgD = PhotoImage(file="images/WD.gif")
wattImgL = PhotoImage(file="images/WL.gif")
wattImg = wattImgL
wattLabel = getMetricLabel(wattImgL, programFrame)
wattLabel.pack(fill=BOTH, expand=True, side=LEFT)
wattLabel.configure(text='0')
colorWidgets.append(wattLabel)
colorImages.append((wattLabel, wattImgD, wattImgL))

standImgD = PhotoImage(file="images/PD.gif")
standImgL = PhotoImage(file="images/PL.gif")
print(standImgL)
standImg = standImgL
standLabel = getMetricLabel(standImgL, programFrame)
standLabel.pack(fill=BOTH, expand=True, side=LEFT)
standLabel.configure(text='Sit')
colorWidgets.append(standLabel)
colorImages.append((standLabel, standImgD, standImgL))

nextImgD = PhotoImage(file="images/ND.gif")
nextImgL = PhotoImage(file="images/NL.gif")
nextImg = nextImgL
durationLabel = getMetricLabel(nextImgL, programFrame)
durationLabel.pack(fill=BOTH, expand=True, side=LEFT)
durationLabel.configure(text='00:00:00')
colorWidgets.append(durationLabel)
colorImages.append((durationLabel, timerImgD, timerImgL))

contentImg = PhotoImage(file="images/RM1.gif")
contentLabel = tk.Label(imageFrame, compound = CENTER, bg='Blue')
contentLabel.pack(fill=Y, expand=True)
contentLabel.config(image=contentImg)
colorWidgets.append(contentLabel)

contentText = tk.Label(textFrame, fg='White', bg='blue', font = "Helvetica 30 bold", padx = 20, pady = 20, anchor = E, text='Test Layout')
contentText.pack(fill=BOTH, expand=True)
colorWidgets.append(contentText)



createLeaderBoard()

for control, lightImage, darkImage in colorImages:
    print(control, lightImage, darkImage)

counter_label(timer)

getRiderInput(leaderBoardFrame)



root.mainloop()