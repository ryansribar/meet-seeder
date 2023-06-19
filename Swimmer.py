from multipledispatch import dispatch


# Swimmer object
# Attributes: str first_name, str last_name, str team, int age, int gender (0 for male), list of int times (index 0 for
# free 1 for back, etc.), list of int events (0 for free, 1 for back, etc.), list of int tentative_events (used during
# seeding process), int num_events
class Swimmer:
    @dispatch(str, str, str, int, int)
    def __init__(self, first_name, last_name, team, age, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.team = team
        self.age = age
        self.gender = gender
        self.times = [None, None, None, None]
        self.events = []
        self.tentative_events = []
        self.num_events = 0

    # Initialize like this for the list of swimmers that are going to be gone
    @dispatch(str, str)
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    # Swimmers are equal when their first and last names are the same
    def __eq__(self, other):
        if self is None or other is None:
            return 0
        return self.first_name == other.first_name and self.last_name == other.last_name

    # Print the first and last name of the swimmer separated by a space
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def set_time(self, event, time):
        if event == "Freestyle" or event == 0:
            self.times[0] = int(time)
        elif event == "Backstroke" or event == 1:
            self.times[1] = int(time)
        elif event == "Breaststroke" or event == 2:
            self.times[2] = int(time)
        elif event == "Butterfly" or event == 3:
            self.times[3] = int(time)
        else:
            raise Exception("Error importing a swimmer's time. Swimmer name: {}, event: {}".format(self, event))

    def set_tentative_events(self, events):
        self.tentative_events = events

    def get_age_group(self):
        if self.age < 9:
            return 0
        elif self.age < 11:
            return 2
        elif self.age < 13:
            return 4
        elif self.age < 15:
            return 6
        return 8

    def get_gender(self):
        return self.gender

    def get_team(self):
        return self.team

    def get_other_team(self):
        if self.team == "Shouse":
            return "Other"
        else:
            return "Shouse"

    def get_num_events(self):
        return int(self.num_events)

    def get_tentative_events(self):
        return self.tentative_events

    def get_time(self, event):
        return self.times[event]

    def add_tentative_event(self, event):
        self.tentative_events.append(event)

    def seed(self, event):
        self.events.append(event)
        if event in self.tentative_events:
            self.tentative_events.remove(event)
        self.num_events += 1

    def is_valid(self):
        return self.num_events + len(self.tentative_events) < 3
