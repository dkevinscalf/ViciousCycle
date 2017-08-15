import time
import CyclingRider

riderList = []

dummyPacket = "020106130038R1R24605P1P20D0004270100GR"

with open('BikeConfig.txt', 'rt') as csvfile:
    for line in csvfile.readlines():
        line = line.replace("\n", "")
        if len(line) > 1:
            lineParts = line.split(',')
            print(lineParts)
            if lineParts[3] == "1":
                riderList.append(CyclingRider.CRider(lineParts[1], 100, 11, 100, int(lineParts[2]), lineParts[0]))

def simulatePacket(rider, file):
    rpmHex = _tohex(rider.RPM*10)
    rpm1 = rpmHex[2:]
    rpm2 = rpmHex[:2]
    packet = dummyPacket.replace("R1",rpm1).replace("R2",rpm2)

    wattHex = _tohex(rider.Power)
    watt1 = wattHex[2:]
    watt2 = wattHex[:2]
    packet = packet.replace("P1",watt1).replace("P2",watt2)

    gear = _tosmallhex(rider.Gear)
    packet = packet.replace("GR",gear)

    print(rider.BikeID, packet)

    file.write(rider.BikeID + "," + packet + "\n")

def _tohex(int_value):
    return format(int_value, '#06x').replace("0x","")

def _tosmallhex(int_value):
    return format(int_value, '#04x').replace("0x","")

while True:
    file = open("BikeData.txt","w")

    for rider in riderList:
        rider.Simulate()
        simulatePacket(rider, file)

    file.close()

    time.sleep(0.1)