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
    if type == "ACTIVITY":
        return CEventType.ACTIVITY
    if type == "MUSIC":
        return CEventType.MUSIC
    if type == "IMAGE":
            return CEventType.IMAGE
    if type == "TEXT":
        return CEventType.TEXT


