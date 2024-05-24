from multipledispatch import dispatch
from Enums import Team, Gender, AgeGroup
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

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return self.__str__()

    def set_time(self, event, time):
        self.events.set_time(event, time)

    def get_age_group(self):
        if self.age < 9:
            return AgeGroup.EIGHT_UNDER
        elif self.age < 11:
            return AgeGroup.NINE_TEN
        elif self.age < 13:
            return AgeGroup.ELEVEN_TWELVE
        elif self.age < 15:
            return AgeGroup.THIRTEEN_FOURTEEN
        return AgeGroup.FIFTEEN_EIGHTEEN

    def get_gender(self):
        return self.gender

    def get_team(self):
        return self.team

    def get_other_team(self):
        return Team.AWAY if self.team == Team.HOME else Team.HOME

    def get_time(self, event):
        return self.events.get_time(event)

    def get_name(self):
        return f'{self.first_name} {self.last_name}'

    def get_events(self):
        return self.events
