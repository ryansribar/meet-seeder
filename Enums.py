from enum import Enum


class Team(Enum):
    HOME = "home"
    AWAY = "away"


class Gender(Enum):
    MALE = 1
    FEMALE = 2


class Event(Enum):
    FREESTYLE = "free"
    BACKSTROKE = "back"
    BREASTSTROKE = "breast"
    BUTTERFLY = "fly"

    # Function to convert from an event string to an Event
    @staticmethod
    def get_event(event_str):
        if event_str == "Freestyle":
            return Event.FREESTYLE
        elif event_str == "Backstroke":
            return Event.BACKSTROKE
        elif event_str == "Breaststroke":
            return Event.BREASTSTROKE
        elif event_str == "Butterfly":
            return Event.BUTTERFLY
        else:
            return None

class Group(Enum):
    EIGHT_UNDER = 1
    NINE_TEN = 2
    ELEVEN_TWELVE = 3
    THIRTEEN_FOURTEEN = 4
    FIFTEEN_EIGHTEEN = 5
