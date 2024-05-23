from Enums import Event


class Events:
    def __init__(self):
        self.freestyle_time = None
        self.backstroke_time = None
        self.breaststroke_time = None
        self.butterfly_time = None

    def get_time(self, event):
        if event == Event.FREESTYLE:
            return self.freestyle_time
        elif event == Event.BACKSTROKE:
            return self.backstroke_time
        elif event == Event.BREASTSTROKE:
            return self.breaststroke_time
        else:
            return self.butterfly_time

    def set_time(self, event, time):
        if event == Event.FREESTYLE:
            self.freestyle_time = time
        elif event == Event.BACKSTROKE:
            self.backstroke_time = time
        elif event == Event.BREASTSTROKE:
            self.breaststroke_time = time
        else:
            self.butterfly_time = time
