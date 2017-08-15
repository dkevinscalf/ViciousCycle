class CActivity:
    Name = ""
    RPM = 0
    WattRate = 0
    Stand = False
    Duration = 0
    
    def __init__(self, name, rpm, wattrate, stand, duration):
        self.Name = name
        self.RPM = rpm
        self.WattRate = wattrate
        self.Stand = stand
        self.Duration = duration

def GetActivityFromActionParams(params):
    paramList = params.split(',')
    return CActivity(paramList[0],paramList[1],paramList[2],paramList[3],paramList[4])