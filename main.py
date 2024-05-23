from Swimmer import Swimmer
import requests
from bs4 import BeautifulSoup
from multipledispatch import dispatch
from ImportData import ImportData
from Enums import Team


# Improvements:
# 1. UI
# 2. Swimming Up
# 3. Making notes for swimmers that just got placed in an event because it did not matter where they went
# 4. Choice to also take times from last year for the other team (would make sure that the swimmer has swum this year)
# 5. Correct score if there is a tie
# 6. Stop swimmers from a team from getting added to an event once that team has three swimmers in that event
# 7. Make the csv parsing not use given indexes for each part, instead find the right index based on the first line of
# the csv file
# 8. Make notes for psych monster

# Logic is wrong for the Nicholas scenario, need to check if there are swimmers that can replace him and if he is close
# to beating the other swimmer in the other event
# Need to check if people are likely to beat the swimmer in second in the Max scenario


# Imports data from the myNVSL website, returns a list of swimmers
# Takes the first, second, third, and fourth parts of the link; the parts in between are updated to get the correct link
# for each age-group/gender/event
@dispatch(str, str, str, str)
def import_data(first, second, third, fourth):
    swimmer_list = []
    url = first
    for age in range(1, 6):
        # Update the url with the age then add the second part
        url += str(age) + second
        for gender in range(1, 3):
            # Update the url with the gender then add the third part
            url += str(gender) + third
            for event in range(4):
                # Update the url with the event/distance
                if age < 2 or (age == 2 and event == 3):
                    url += "25-"
                else:
                    url += "50-"
                if event == 0:
                    url += "free"
                elif event == 1:
                    url += "back"
                elif event == 2:
                    url += "breast"
                elif event == 3:
                    url += "fly"
                url += fourth
                webpage = requests.get(url)
                soup = BeautifulSoup(webpage.content, "html.parser")
                # the way the website does it is weird, there is a different class depending on if the swimmer has an
                # odd or even place ranking, so there is two lists
                swimmer_list_odds = soup.findAll(class_="odd")
                swimmer_list_evens = soup.findAll(class_="even")
                for swimmer in swimmer_list_odds:
                    add_swimmer(swimmer_list, swimmer, gender, event)
                for swimmer in swimmer_list_evens:
                    add_swimmer(swimmer_list, swimmer, gender, event)
                # Get the same url but without the last part to generate a new one
                url = first + str(age) + second + str(gender) + third
            # Get the same url but without the last two parts to generate a new one
            url = first + str(age) + second
        print(".", end='')
        url = first
    return swimmer_list


# Adds the given swimmer and to the swimmer_list and/or updates their time in the event
def add_swimmer(swimmer_list, swimmer_element, gender, event):
    index = 0
    gender -= 1
    first_name = ""
    last_name = ""
    team = "Other"
    age = 0
    time = None
    for element in swimmer_element.findAll("td"):
        # index 1 is the time
        if index == 1:
            # split the string in case of a time > 1 minute
            temp = element.string.split(":")
            if len(temp) > 1:
                time = int(temp[0]) * 6000 + int(float(temp[1]) * 100)
            else:
                time = int(float(element.string) * 100)
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


# Create Ladders:
# Takes a list of swimmers and creates a list of ladders such that ladder_list[0] is 8&Under Boys, ladder_list[1] is
# 8&Under Girls, etc. Each ladder is a list of the four events such that ladder[0] is Freestyle, ladder[1] is Backstroke
# To do this, each swimmer is taken and placed in the ladder based on their time in that event, if they have no time
# they are placed at the bottom of the ladder
def create_ladders(swimmer_list):
    ladder_list = []
    for swimmer_grouping in range(10):
        ladder_list.append([])
        for event in range(4):
            ladder_list[swimmer_grouping].append([])
    for swimmer in swimmer_list:
        ladder = ladder_list[swimmer.get_age_group() + swimmer.get_gender()]
        for event in range(4):
            event_ladder = ladder[event]
            time = swimmer.get_time(event)
            # If the swimmer has no time add them to the end of the ladder
            if time is None:
                event_ladder.append(swimmer)
            # If they do have a time, find the first spot in the ladder that they are faster than someone or the first
            # occurrence of None
            else:
                rank = 0
                while rank < len(event_ladder):
                    other_time = event_ladder[rank].get_time(event)
                    if other_time is None or time < other_time:
                        break
                    rank += 1
                event_ladder.insert(rank, swimmer)
    return ladder_list


# Clean ladders:
# Takes a list of ladders and "cleans" it by removing all occurrences of swimmers in swimmer_list from the ladder
# Returns the cleaned ladders in a list
def clean_ladders(ladder_list, swimmer_list):
    absent_list = ["Ben Phillips", "James Garver", "Elliot Rhines", "Katelyn Armstrong", "Chloe Gao",
                   "Charles Williams"]
    flag = 0
    for swimmer_name in absent_list:
        name = swimmer_name.split(" ")
        swimmer = Swimmer(name[0], name[1])
        if swimmer not in swimmer_list:
            print("\nPotential wrong spelling for name: {}".format(swimmer_name), end='')
            flag = 1
        else:
            swimmer = swimmer_list[swimmer_list.index(swimmer)]
            ladder = ladder_list[swimmer.get_age_group() + swimmer.get_gender()]
            for event in range(4):
                ladder[event].remove(swimmer)
    if flag:
        print()
    return ladder_list


# Seeding:
# Takes a complete list of ladders for each gender/age-group of the other team combined with the Shouse swimmers that
# declared yes
# Isolates each ladder for a gender/age-group and "trims" it
def seed(ladder_list):
    for ladder in ladder_list:
        trim(ladder)
    return ladder_list


# Trimming a ladder:
# Takes a ladder for a gender/age-group and "trims" it, returns the trimmed ladder
# To trim a ladder:
# 1. Start by assuming each swimmer will be seeded in every event that they are listed in on the ladder
# 2. Go by place; add each event to the tentative event list for the swimmer in that place
# 3. Go by event in the place that was just seeded: If a swimmer is in < 3 events, add their tentative event list to
# their actual event list.
# 3.5. If they are now in 2 events, remove them from the ladder in the other 2 events
# 4. If the swimmer is in > two events, look at the places below the events that are conflicting in the lowest
# place the swimmer is in
# 5. Seed the swimmer in the event(s) that a swimmer from the other team is ranked the highest below the place of the
# tentative swimmer, this way those swimmers are prevented from getting more points
# 6. If the swimmers' teams in the places below the tentative swimmer are all the same, go to the first occurrence of a
# swimmer on the other team and seed the tentative swimmer in the event that the swimmer above them is supposed to beat
# them by the least
# 6.5 If the first occurrence of the other team is the place directly below the tentative swimmer, seed the tentative
# swimmer in the place where they are supposed to win by the most
# 7. Once a swimmer is seeded in a place, they are locked in to that event because they will score the most points there
def trim(ladder):
    event_indexes = [0, 0, 0, 0]
    for place in range(10):
        # Get the swimmer at the place/event in the ladder and add that event to their tentative list of events
        for event in range(4):
            if place >= len(ladder[event]):
                break
            swimmer = ladder[event][event_indexes[event]]
            swimmer.add_tentative_event(event)
        # Go through the place that was just seeded and check to make sure each swimmer is valid (in < 2 events)
        for event in range(4):
            if place >= len(ladder[event]):
                break
            swimmer = ladder[event][event_indexes[event]]
            # If they are valid, seed them in the event(s) they are tentatively in
            if swimmer.is_valid():
                # If they are not already seeded, seed them in the event
                if swimmer.get_num_events() != 2:
                    swimmer.seed(event)
                    event_indexes[event] += 1
                # If they are now in two events, remove them from the ladder
                if swimmer.get_num_events() == 2:
                    remove_from_ladder(swimmer, ladder)
            # If they are not valid, look at the events that are conflicting (tentative_events) and look at the teams of
            # the swimmers below the tentative swimmer in those events
            else:
                place_index = place + 1
                tentative_events = []
                # Loop until 6th place is reached, break manually if they become valid
                while place_index < 6:
                    tentative_events = swimmer.get_tentative_events().copy()
                    teams = [None, None, None, None]
                    same_count = 0
                    other_count = 0
                    for tentative_event in tentative_events:
                        # Check to make sure there is a swimmer here in the ladder
                        if place_index < len(ladder[tentative_event]):
                            team = ladder[tentative_event][place_index].team
                            if team == swimmer.get_team():
                                same_count += 1
                            else:
                                other_count += 1
                            teams[tentative_event] = team
                    # If there were no swimmers in the ladder below the tentative swimmer, break out of the loop
                    if same_count == 0 and other_count == 0:
                        break
                    # If all the teams match up, keep going down the places
                    if same_count == 0 or other_count == 0:
                        pass
                    # If there is 1 event with swimmers on the other team beneath where this swimmer is seeded, seed the
                    # swimmer in that event
                    elif other_count == 1:
                        swimmer.seed(teams.index(swimmer.get_other_team()))
                        event_indexes[teams.index(swimmer.get_other_team())] += 1
                    else:
                        # If there are just two events with swimmers from the other team at this place, seed the
                        # tentative swimmer in those two events and remove any other tentative events
                        if other_count == 2 and swimmer.get_num_events() == 0:
                            for i in range(2):
                                swimmer.seed(teams.index(swimmer.get_other_team()))
                                event_indexes[teams.index(swimmer.get_other_team())] += 1
                                teams[teams.index(swimmer.get_other_team())] = None
                            swimmer.set_tentative_events([])
                        # Otherwise remove the tentative events that have swimmers from the same team below the
                        # tentative swimmer, then set the tentative events to the events that are left
                        else:
                            for i in range(same_count):
                                tentative_events.remove(teams.index(swimmer.get_team))
                                teams[teams.index(swimmer.get_team())] = None
                            swimmer.set_tentative_events(tentative_events)
                    place_index += 1
                    if swimmer.is_valid():
                        break
                # Check to see if the loop broke because they are now valid or because it got to 6th place
                # If they are not valid, go to the first occurrence of the other team below the place that the tentative
                # events are and compare the times
                if not swimmer.is_valid():
                    time_differences = [None, None, None, None]
                    other_team_place = find_other_team_place(swimmer, ladder, place)
                    # Check for the other team having a swimmer below the tentative one
                    if other_team_place != 0:
                        for tentative_event in tentative_events:
                            time_differences[tentative_event] = ladder[tentative_event][other_team_place] \
                                .get_time(tentative_event)
                            if time_differences[tentative_event] is None:
                                time_differences[tentative_event] = -99999
                            else:
                                time_differences[tentative_event] -= ladder[tentative_event][other_team_place - 1] \
                                    .get_time(tentative_event)
                        time_differences_sorted = time_differences.copy()
                        time_differences_sorted = [x for x in time_differences_sorted if x is not None]
                        time_differences_sorted.sort()
                        # If the other teams place is directly below the tentative swimmer, reverse the list so that
                        # they are seeded in the event they are winning by the most instead of the least
                        if place + 1 == other_team_place:
                            time_differences_sorted.reverse()
                        time_list_index = 0
                        while swimmer.get_num_events() != 2:
                            swimmer.seed(time_differences.index(time_differences_sorted[time_list_index]))
                            time_list_index += 1
                    # If there is no swimmer on the other team in the places below the tentative swimmer, just seed them
                    # by the order of their tentative event list because it doesn't matter where they go
                    else:
                        tentative_event_index = 0
                        while swimmer.get_num_events() != 2:
                            swimmer.seed(swimmer.get_tentative_events()[tentative_event_index])
                            tentative_event_index += 1
                remove_from_ladder(swimmer, ladder)
    return ladder


# Remove swimmer from ladder:
# Takes a swimmer and the ladder for their gender/age-group and removes them from the ladder in the events not listed in
# their event list
def remove_from_ladder(swimmer, ladder):
    events = [0, 1, 2, 3]
    for event in swimmer.get_events():
        events.remove(event)
    for event in events:
        if swimmer in ladder[event]:
            ladder[event].remove(swimmer)


# Find the first occurrence of the other team starting at place in the ladder in the tentative events for the swimmer
# Returns 0 if there are no occurrences, otherwise returns the place of the occurrence
def find_other_team_place(swimmer, ladder, place):
    event = swimmer.get_tentative_events()[0]
    for i in range(place, len(ladder[event])):
        if ladder[event][place].get_team != swimmer.get_team:
            return place
    return 0


# Calculates the expected score of the meet after the individual events
# Takes the seeds of the meet and returns a list of two scores, the first being the shouse score
def calculate_score(seeds):
    scores = [0, 0]
    scores_list = [5, 3, 1]
    for ladder in seeds:
        for event in ladder:
            for place in range(3):
                if place < len(event):
                    team = event[place].get_team()
                    if team == "Shouse":
                        scores[0] += scores_list[place]
                    else:
                        scores[1] += scores_list[place]
    return scores


def main():
    print("Importing Home times.....", end='')
    swimmer_list = ImportData.import_from_csv('shouse_times.csv', Team.HOME)
    print("Done")

    print("Importing other team times", end='')
    swimmer_list_2 = ImportData.import_from_myNVSL(Team.AWAY, 261)
    print("Done")
    print(swimmer_list_2)

    print("Creating ladders.....", end='')
    ladder_list = create_ladders(swimmer_list)
    print("Done")

    print("Cleaning ladders.....", end='')
    cleaned_ladder_list = clean_ladders(ladder_list, swimmer_list)
    print("Done")

    print("Seeding meet.....", end='')
    seeds = seed(cleaned_ladder_list)
    print("Done")

    print("\n----------------------------------------")
    age_groups = ["8&Under Boys", "8&Under Girls", "9-10 Boys", "9-10 Girls", "11-12 Boys", "11-12 Girls", "13-14 Boys",
                  "13-14 Girls", "15-18 Boys", "15-18 Girls"]
    events = ["Freestyle", "Backstroke", "Breaststroke", "Butterfly"]
    age_group_index = 0
    for ladder in seeds:
        print("{}:".format(age_groups[age_group_index]))
        event_index = 0
        for event in ladder:
            print("{}: ".format(events[event_index]))
            count = 0
            shouse_count = 0
            other_count = 0
            for swimmer in event:
                team = swimmer.get_team()
                if team == "Shouse":
                    shouse_count += 1
                    if shouse_count < 4:
                        count += 1
                        print("{}: {}".format(swimmer, swimmer.get_time(event_index)))
                else:
                    other_count += 1
                    if other_count < 4:
                        count += 1
                        print("{}: {}".format(swimmer, swimmer.get_time(event_index)))
                if count > 5:
                    break
            event_index += 1
            if ladder.index(event) != len(ladder) - 1:
                print()
        age_group_index += 1
        print("----------------------------------------")

    print("Calculating scores.....")
    scores = calculate_score(seeds)
    print("Shouse: {}".format(scores[0]))
    print("Other team: {}".format(scores[1]))


main()
