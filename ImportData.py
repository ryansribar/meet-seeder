import csv
import requests
from bs4 import BeautifulSoup
from Enums import Gender, Event, AgeGroup
from Swimmer import Swimmer
from Time import Time


class ImportData:
    # Return: a list of Swimmer objects
    # Parameters: String filename (must have the .csv extension), Team team
    # The Swimmer list will contain all swimmers in the file
    # See "shouse_times.csv" for an example csv file
    @staticmethod
    def import_from_csv(filename, team):
        swimmer_list = []
        with open(filename) as csvfile:
            data_file = csv.reader(csvfile, delimiter=',')
            data_file.__next__()
            for row in data_file:
                swimmer = get_swimmer_from_csv_row(row, team)
                if swimmer not in swimmer_list:
                    swimmer_list.append(swimmer)
                swimmer = swimmer_list[swimmer_list.index(swimmer)]
                event = Event.get_event(row[10])
                if event:
                    time = row[3]
                    swimmer.set_time(event, time)
        return swimmer_list

    # Return: a list of Swimmer objects
    # Parameters: Team team, int team_num (See README for where to find a team number)
    # The list will contain all swimmers on the given team with an official NVSL time
    @staticmethod
    def import_from_myNVSL(team, team_num):
        swimmer_list = []
        for age_group in AgeGroup:
            for gender in Gender:
                for event in Event:
                    url = generate_url(team_num, age_group, event, gender)
                    webpage = requests.get(url)
                    soup = BeautifulSoup(webpage.content, "html.parser")

                    # the way the website does it is weird, there is a different class depending on if the swimmer has
                    # an odd or even place ranking, so there are two lists
                    swimmer_list_odds = soup.findAll(class_="odd")
                    swimmer_list_evens = soup.findAll(class_="even")
                    for swimmer_element in swimmer_list_odds:
                        update_swimmer_list(swimmer_list, swimmer_element, gender, event, team)
                    for swimmer_element in swimmer_list_evens:
                        update_swimmer_list(swimmer_list, swimmer_element, gender, event, team)
            print(".", end='')
        return swimmer_list


# Return: a Swimmer object
# Parameters: List row, Team team
# Helper method to parse a row of data from a csv, returns a swimmer
def get_swimmer_from_csv_row(row, team):
    gender = Gender.MALE if "Boys" in row[0] or "Men" in row[0] else Gender.FEMALE
    last_name = row[5]
    first_name = row[6]
    age = int(row[7])
    return Swimmer(first_name, last_name, team, age, gender)


# Return: None
# Parameters: List swimmer_list, [HTML element?] swimmer_element, Gender gender, Event event, Team team
# Adds the given swimmer to the swimmer_list if they are not already there, also updates their time in the event
def update_swimmer_list(swimmer_list, swimmer_element, gender, event, team):
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
        index += 1
    swimmer = Swimmer(first_name, last_name, team, age, gender)
    if swimmer not in swimmer_list:
        swimmer_list.append(swimmer)
    swimmer = swimmer_list[swimmer_list.index(swimmer)]
    swimmer.set_time(event, time)


# Return: a URL linking to a specific Team's myNVSL page
# Parameters: int team_num, AgeGroup age_group, Event event, Gender gender
# Generate a link to the myNVSL page containing the times for the given team, age group, event, and gender
def generate_url(team_num, age_group, event, gender):
    myNVSL_link_age = "https://www.mynvsl.com/leaders?post=1&mt=0&age="
    myNVSL_link_sex = "&sex="
    myNVSL_link_stroke = "&st=1&stroke="
    myNVSL_link_team = "&m=1&year=2023&count=25&division=&team="
    link = f'{myNVSL_link_age}{str(age_group.value)}'
    link += f'{myNVSL_link_sex}{str(gender.value)}'
    distance = "25" if age_group == AgeGroup.EIGHT_UNDER else "50"
    link += f'{myNVSL_link_stroke}{distance}-{event.value}'
    link += f'{myNVSL_link_team}{str(team_num)}'
    return link
