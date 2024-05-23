import csv
import requests
from bs4 import BeautifulSoup
from Enums import Gender, Event, Group
from Swimmer import Swimmer
from Time import Time


class ImportData:
    MYNVSL_LINK_AGE = "https://www.mynvsl.com/leaders?post=1&mt=0&age="
    MYNVSL_LINK_SEX = "&sex="
    MYNVSL_LINK_STROKE = "&st=1&stroke="
    MYNVSL_LINK_TEAM = "&m=1&year=2023&count=25&division=&team="

    # See "shouse_times.csv" for an example csv file
    @staticmethod
    def import_from_csv(filename, team):
        swimmer_list = []
        with open(filename) as csvfile:
            data_file = csv.reader(csvfile, delimiter=',')
            data_file.__next__()
            for row in data_file:
                swimmer = ImportData.get_swimmer_from_row(row, team)
                if swimmer not in swimmer_list:
                    swimmer_list.append(swimmer)
                else:
                    swimmer = swimmer_list[swimmer_list.index(swimmer)]
                event = Event.get_event(row[10])
                if event:
                    time = row[3]
                    swimmer.set_time(event, time)
        return swimmer_list

    # Helper function to parse a row of data from a csv, returns a swimmer
    @staticmethod
    def get_swimmer_from_row(row, team):
        gender = Gender.MALE if "Boys" in row[0] or "Men" in row[0] else Gender.FEMALE
        last_name = row[5]
        first_name = row[6]
        age = int(row[7])
        return Swimmer(first_name, last_name, team, age, gender)

    # Imports data from the myNVSL website, returns a list of swimmers
    @staticmethod
    def import_from_myNVSL(team, team_num):
        swimmer_list = []
        for age_group in Group:
            for gender in Gender:
                for event in Event:
                    url = ImportData.generate_url(ImportData, team_num, age_group, event, gender)
                    webpage = requests.get(url)
                    soup = BeautifulSoup(webpage.content, "html.parser")
                    # the way the website does it is weird, there is a different class depending on if the swimmer has
                    # an odd or even place ranking, so there are two lists
                    swimmer_list_odds = soup.findAll(class_="odd")
                    swimmer_list_evens = soup.findAll(class_="even")
                    for swimmer in swimmer_list_odds:
                        ImportData.add_swimmer(swimmer_list, swimmer, gender, event, team)
                    for swimmer in swimmer_list_evens:
                        ImportData.add_swimmer(swimmer_list, swimmer, gender, event, team)
            print(".", end='')
        return swimmer_list

    # Adds the given swimmer and to the swimmer_list and/or updates their time in the event
    @staticmethod
    def add_swimmer(swimmer_list, swimmer_element, gender, event, team):
        index = 0
        first_name = ""
        last_name = ""
        age = 0
        time = None
        for element in swimmer_element.findAll("td"):
            # index 1 is the time
            if index == 1:
                time = Time(element.string)
            # index 2 is the swimmer name
            elif index == 2:
                name = element.string.split()
                first_name = name[0]
                # some names include the middle initial, so check for that
                if len(name) > 2:
                    last_name = name[2]
                else:
                    last_name = name[1]
            # index 3 is the age
            elif index == 3:
                age = int(element.string)
                # convert old 25 times to 50s
                '''
                if age == 8:
                    for event in range(3):
                        if swimmer.get_time(event) is not None:
                            swimmer.set_time(event, swimmer.get_time(event) * 2.2)
                if age == 10:
                    if swimmer.get_time(3) is not None:
                        swimmer.set_time(3, swimmer.get_time(3) * 2.2)
                '''
            index += 1
        swimmer = Swimmer(first_name, last_name, team, age, gender)
        if swimmer not in swimmer_list:
            swimmer_list.append(swimmer)
        else:
            swimmer = swimmer_list[swimmer_list.index(swimmer)]
        swimmer.set_time(event, time)

    # Generate a link to the myNVSL page containing the times for the given team, age group, event, gender
    # As parameters, it takes an int team number, Enums.Group, Enums.Event, and Enums.Gender
    @staticmethod
    def generate_url(self, team_num, age_group, event, gender):
        link = f'{self.MYNVSL_LINK_AGE}{str(age_group.value)}'
        link += f'{self.MYNVSL_LINK_SEX}{str(gender.value)}'
        distance = "25" if age_group == Group.EIGHT_UNDER else "50"
        link += f'{self.MYNVSL_LINK_STROKE}{distance}-{event.value}'
        link += f'{self.MYNVSL_LINK_TEAM}{str(team_num)}'
        return link

