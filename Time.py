# Used for not having to write all the comparison methods
from functools import total_ordering
# Regex
import re
# Used for function overriding
from multipledispatch import dispatch


# Time object
# Attributes: int minutes; int seconds; int milliseconds
@total_ordering
class Time:
    @dispatch(str)
    def __init__(self, time):
        self.get_time_from_string(time)

    @dispatch(int, int, int)
    def __init__(self, minutes, seconds, milliseconds):
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    @dispatch(int)
    def __init__(self, time):
        self.milliseconds = time % 100
        seconds = (time // 100)
        self.seconds = seconds % 60
        self.minutes = seconds // 60

    def __eq__(self, other):
        return self.minutes == other.minutes and self.seconds == other.seconds \
            and self.milliseconds == other.milliseconds

    def __lt__(self, other):
        if self.minutes < other.minutes:
            return True
        elif self.minutes > other.minutes:
            return False
        elif self.seconds < other.seconds:
            return True
        elif self.seconds > other.seconds:
            return False
        elif self.milliseconds < other.milliseconds:
            return True
        else:
            return False

    def __str__(self):
        time = f'{self.seconds}.0{self.milliseconds}' if self.milliseconds < 10 \
            else f'{self.seconds}.{self.milliseconds}'
        if self.minutes == 0:
            return time
        else:
            return f'{self.minutes}:{time}'

    def __add__(self, other):
        tot_milliseconds = self.milliseconds + other.milliseconds
        tot_seconds = self.seconds + other.seconds + (tot_milliseconds // 100)
        new_milliseconds = tot_milliseconds % 100
        new_seconds = (tot_seconds % 60)
        new_minutes = self.minutes + other.minutes + (tot_seconds // 60)

    # Might have to edit this function because it is getting the time and setting in the same function, violating the
    # SRP
    def get_time_from_string(self, time):
        pattern = r"(?:(\d+):)?(\d{2})\.(\d{2})"
        match = re.match(pattern, time)
        if match:
            minutes, seconds, milliseconds = match.groups()
            self.minutes = int(minutes) if minutes else 0
            self.seconds = int(seconds)
            self.milliseconds = int(milliseconds) if milliseconds else 0
