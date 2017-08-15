from enum import Enum

import json

class CEventType(Enum):
    ACTIVITY = 1,
    MUSIC = 2,
    IMAGE = 3,
    TEXT = 4

class CEvent:
    time = 0
    fired = False
    actionType = CEventType.ACTIVITY
    actionParams = ""

class CSegment:
    globalStartTime = 0
    name = ""
    events = []

class RoutinePayload(object):
    def __init__(self, j):
        self.__dict__ = json.load(j)

def ConvertIntToEventType(type):
    if type == 1:
        return CEventType.ACTIVITY
    if type == 2:
        return CEventType.MUSIC
    if type == 3:
            return CEventType.IMAGE
    if type == 4:
        return CEventType.TEXT


