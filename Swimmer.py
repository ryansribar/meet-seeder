from multipledispatch import dispatch
from Enums import Event, Team, Gender, Group
from Events import Events


# Swimmer object
# Attributes: String first_name; String last_name; Team team; int age; Gender gender; List of Time times;
# List of Event events;
class Swimmer:
    @dispatch(str, str, Team, int, Gender)
    def __init__(self, first_name, last_name, team, age, gender):
        self.first_name = first_name
        self.last_name = last_name
        self.team = team
        self.age = age
        self.gender = gender
        self.events = Events()

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

    def __repr__(self):
        return self.__str__()

    def set_time(self, event, time):
        self.events.set_time(event, time)

    #    if event == "Freestyle" or event == 0:
    #        self.events.set_time
    #    elif event == "Backstroke" or event == 1:
    #        self.times[1] = int(time)
    #    elif event == "Breaststroke" or event == 2:
    #        self.times[2] = int(time)
    #    elif event == "Butterfly" or event == 3:
    #        self.times[3] = int(time)
    #    else:
    #        raise Exception("Error importing a swimmer's time. Swimmer name: {}, event: {}".format(self, event))

    # def set_tentative_events(self, events):
    #    self.tentative_events = events

    def get_age_group(self):
        if self.age < 9:
            return Group.EIGHT_UNDER
        elif self.age < 11:
            return Group.NINE_TEN
        elif self.age < 13:
            return Group.ELEVEN_TWELVE
        elif self.age < 15:
            return Group.THIRTEEN_FOURTEEN
        return Group.FIFTEEN_EIGHTEEN

    def get_gender(self):
        return self.gender

    def get_team(self):
        return self.team

    def get_other_team(self):
        return Team.HOME if self.team == Team.HOME else Team.AWAY

    def get_num_events(self):
        return int(self.num_events)

    def get_tentative_events(self):
        return self.tentative_events

    def get_time(self, event):
        return self.events.get_time(event)

    def add_tentative_event(self, event):
        self.tentative_events.append(event)

    def get_name(self):
        return self.first_name + " " + self.last_name

    def get_events(self):
        return self.events

    def seed(self, event):
        self.events.append(event)
        if event in self.tentative_events:
            self.tentative_events.remove(event)
        self.num_events += 1

    def is_valid(self):
        return self.num_events + len(self.tentative_events) < 3
