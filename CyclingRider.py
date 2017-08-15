import random 

class CRider:
    RiderName = ''
    RPM = 0
    Gear = 0
    Power = 0
    TargetPower = 0
    BikeID = ''
    RowID = 0
    NameLabel = None
    RPMLabel = None
    WattLabel = None

    def __init__(self, name, rpm, gear, power, targetpower, bikeid):
        self.RiderName = name
        self.RPM = rpm
        self.Gear = gear
        self.Power = power
        self.TargetPower = targetpower
        self.BikeID = bikeid

    def WattPercentage(self):
        return int(self.Power / self.TargetPower * 100)

    def ColorLeaderBoard(self, bgColor, fgColor):
        self.NameLabel.configure(bg= bgColor)
        self.NameLabel.configure(fg= fgColor)
        self.RPMLabel.configure(bg= bgColor)
        self.RPMLabel.configure(fg= fgColor)
        self.WattLabel.configure(bg= bgColor)
        self.WattLabel.configure(fg= fgColor)

    def Simulate(self):
        self.Power += random.randrange(-4,5)
        self.RPM += random.randrange(-1,2)

    def ParseFromBikeData(self, data):
        rpmHex = data[14:16] + data[12:14]
        rpmInt = int(rpmHex,16)
        self.RPM = rpmInt / 10

        powerHex = data[22:24] + data[20:22]
        powerInt = int(powerHex,16)
        self.Power = powerInt

        gearHex = data[36:38]
        self.Gear = int(gearHex,16)


