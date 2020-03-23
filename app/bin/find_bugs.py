from datetime import datetime
import pytz

def main(hemisphere, tz):
    if hemisphere == 'Northern':
        bug_list = load_northern()
    else:
        bug_list = load_southern()
    active_bugs = process_bugs(bug_list, datetime.now(pytz.timezone(tz)))
    return active_bugs

def process_bugs(bugs_list, dt):
    month = dt.month
    hour = dt.hour
    good_bug = []
    for bug in bugs_list:
        seasonality = bug[1]
        times = bug[3]
        good_month = test_seasonality(seasonality, month)
        good_time = test_time(times, hour)
        if good_month and good_time:
            if bug[3] != 'All day':
                bug_times = bug[3].split(' - ')
                bug[3] = bug_times[0] + ':00 - ' + bug_times[1] + ':00'
            good_bug.append([bug[0], bug[2], int(bug[4].replace(',','')), bug[1], bug[3]])
    return sorted(good_bug, key= lambda x:x[2], reverse=True)

def test_seasonality(seasonality, month):
    if seasonality == 'All year':
        return True
    else:
        seasonality = seasonality.split(' | ')
        for season in seasonality:
            season = season.split(' - ')
            date_dict = load_dict()
            if len(season) == 2:
                m1 = date_dict[season[0]]
                m2 = date_dict[season[1]]
                if m1 < m2:
                    if month >= m1 and month <= m2:
                        return True
                    else:
                        return False
                else:
                    if (month >= m1 and month <= 12) or (month < m2 and month >= 1):
                        return True
                    else:
                        return False
                for m in season:
                    if month == load_dict()[m]:
                        return True
            else:
                if month == date_dict[season[0]]:
                    return True
                else:
                    return False
        return False

def test_time(times, hour):
    if times == 'All day':
        return True
    else:
        times = times.split(' | ')
        for t in times:
            t = t.split(' - ')
            t = [ int(tt) for tt in t]
            if t[0] < t[1]:
                if hour >= t[0] and hour < t[1]:
                    return True
                else:
                    return False
            else:
                if (hour >= t[0] and hour < 24) or (hour < t[1] and hour >= 0):
                    return True
                else:
                    return False

def load_northern():
    return [
        ['Agris Butterfly', 'Apr - Sept', 'Flying', '8 - 17', '3,000'],
        ['Ant', 'All year', 'On rotten fruit and turnips', 'All day', '80'],
        ['Bagworm', 'All year', 'Shake tree', 'All day', '600'],
        ['Centipede', 'Sept - June', 'Hit rocks', '17 - 23', '430'],
        ['Citrus Long-Horned Beetle', 'All year', 'Tree stump', 'All day', '350'],
        ['Common Butterfly', 'Sept - June', 'Flying', '4 - 19', '160'],
        ['Cricket', 'Sept - Nov', 'Ground', '17 - 8', '130'],
        ['Damselfly', 'Nov - Feb', 'Flying', 'All day', '500'],
        ['Darner Dragonfly', 'Apr - Oct', 'Flying', '8 - 17', '230'],
        ['Diving Beetle', 'May - Sept', 'River', '8 - 19', '800'],
        ['Dung Beetle', 'Dec - Feb', 'Snowballs', 'All day', '2,500'],
        ['Earth-Boring Dung Beetle', 'July - Sept', 'Ground', 'All day', '300'],
        ['Emperor Butterfly', 'Dec - Mar | June - Sept', 'Flying', '17 - 8', '4,000'],
        ['Flea', 'Apr - Nov', 'On a flea-infested villager', 'All day', '70'],
        ['Fly', 'All year', 'On rotten fruit or garbage', 'All day', '60'],
        ['Grasshopper', 'July - Sept', 'Ground', '8 - 17', '160'],
        ['Hermit Crab', 'All year', 'Beach', '19 - 8', '1,000'],
        ['Honeybee', 'Mar - July', 'Near flowers', '8 - 17', '200'],
        ['Ladybug', 'Mar - June | Oct', 'Flowers', '8 - 17', '200'],
        ['Long Locust', 'Apr - Nov', 'Ground', '8 - 19', '200'],
        ['Madagascan Sunset Moth', 'Apr - Sept', 'Flying', '8 - 16', '2,500'],
        ['Man-Faced Stink Bug', 'Mar - Oct', 'Flowers', '19 - 8', '1,000'],
        ['Mantis', 'Mar - Nov', 'Flowers', '8 - 17', '430'],
        ['Migratory Locust', 'Feb - May', 'Ground', '8 - 19', '200'],
        ['Mole Cricket', 'Nov - May', 'Underground', 'All day', '500'],
        ['Monarch Butterfly', 'Sept - Nov', 'Flying', '4 - 17', '140'],
        ['Mosquito', 'June - Sept', 'Flying', '17 - 4', '130'],
        ['Moth', 'All year', 'Lit windows', '19 - 4', '130'],
        ['Orchid Mantis', 'Mar - Nov', 'Flowers', '8 - 17', '2,400'],
        ['Paper Kite Butterfly', 'All year', 'Flying', '8 - 19', '1,000'],
        ['Peacock Butterfly', 'Mar - June', 'Near black, blue, or purple flowers', '4 - 19', '2,500'],
        ['Pill Bug', 'Sept - June', 'Hit rocks', '23 - 16', '250'],
        ['Pondskater', 'May - Sept', 'River', '8 - 19', '130'],
        ['Queen Alexandra’s Birdwing', 'May - Sept', 'Flying', '8 - 16', '4,000'],
        ['Rainbow Stag', 'June - Sept', 'Tree', '19 - 8', '6,000'],
        ['Rajah Brooke’s Birdwing', 'Dec - Feb | Apr - Sept', 'Near black, blue, or purple flowers', '8 - 17', '2,500'],
        ['Red Dragonfly', 'Sept - Oct', 'Flying', '8 - 19', '180'],
        ['Rosalia Batsei Beetle', 'May - June', 'Tree stump', 'All day', '3,000'],
        # ['Scorpion', 'TBD', 'Ground', 'Night', ''],
        ['Snail', 'All year', 'Rock (rain)', 'All day', '250'],
        ['Spider', 'All year', 'Shake tree', '19 - 8', '600'],
        ['Stinkbug', 'Mar - Oct', 'Flowers', 'All day', '120'],
        ['Tarantula', 'Nov - Apr', 'Ground', '19 - 4', '8,000'],
        ['Tiger Beetle', 'Feb - Oct', 'Ground', 'All day', '1,500'],
        ['Tiger Butterfly', 'Mar - Sept', 'Flying', '4 - 19', '240'],
        ['Violin Beetle', 'May - June | Sept - Nov', 'Tree stump', 'All day', '450'],
        ['Walker Cicada', 'Aug - Sept', 'Tree', '8 - 16', '400'],
        ['Walking Leaf', 'July - Sept', 'Ground', 'All day', '600'],
        ['Wasp', 'All year', 'Shake tree', 'All day', '2,500'],
        ['Wharf Roach', 'All year', 'Beach (rocks)', 'All day', '200'],
        ['Yellow Butterfly', 'Mar - June | Sept - Oct', 'Flying', '4 - 19', '160']]

def load_southern():
    return [
        ['Agris Butterfly', 'Oct - Mar', 'Flying', '8 - 17', '3,000'],
        ['Ant', 'All year', 'Rotten fruit or turnips', 'All day', '80'],
        ['Bagworm', 'All year', 'Shake tree', 'All day', '600'],
        ['Centipede', 'Mar - Dec', 'Hit rocks', 'All day', '430'],
        ['Citrus Long-Horned Beetle', 'All year', 'Tree stump', 'All day', '350'],
        ['Common Butterfly', 'Mar - Dec', 'Flying', '4 - 19', '160'],
        ['Cricket', 'Mar - May', 'Ground', '17 - 8', '130'],
        ['Damselfly', 'May - Aug', 'Flying', 'All day', '500'],
        ['Darner Dragonfly', 'Oct - Apr', 'Flying', '8 - 17', '230'],
        ['Diving Beetle', 'Nov - Mar', 'River', '8 - 19', '800'],
        ['Dung Beetle', 'June - Aug', 'Snowballs', 'All day', '2,500'],
        ['Earth-Boring Dung Beetle', 'Jan - Mar', 'Ground', 'All day', '300'],
        ['Emperor Butterfly', 'Dec - Mar | June - Sept', 'Flying', '17 - 8', '4,000'],
        ['Flea', 'Oct - May', 'On a flea-infested Villager', 'All day', '70'],
        ['Fly', 'All year', 'On rotten fruit or garbage', 'All day', '60'],
        ['Grasshopper', 'Jan - Mar', 'Ground', '8 - 17', '160'],
        ['Hermit Crab', 'All year', 'Beach', '19 - 8', '1,000'],
        ['Honeybee', 'Sept - Jan', 'Near flowers', '8 - 17', '200'],
        ['Ladybug', 'Apr | Sept - Dec', 'Flowers', '8 - 17', '200'],
        ['Long Locust', 'Oct - May', 'Ground', '8 - 19', '200'],
        ['Madagascan Sunset Moth', 'Oct - Mar', 'Flying', '8 - 16', '2,500'],
        ['Man-Faced Stink Bug', 'Sept - Apr', 'Flowers', '19 - 8', '1,000'],
        ['Mantis', 'Sept - Apr', 'Flowers', '8 - 17', '430'],
        ['Migratory Locust', 'Feb - May', 'Ground', '8 - 19', '200'],
        ['Mole Cricket', 'May - Nov', 'Underground', 'All day', '500'],
        ['Monarch Butterfly', 'Mar - May', 'Flying', '4 - 17', '140'],
        ['Mosquito', 'Dec - Mar', 'Flying', '17 - 4', '130'],
        ['Moth', 'All year', 'Lit windows', '19 - 4', '130'],
        ['Orchid Mantis', 'Sept - May', 'Flowers', '8 - 17', '2,400'],
        ['Paper Kite Butterfly', 'All year', 'Flying', '8 - 19', '1,000'],
        ['Peacock Butterfly', 'Sept - Dec', 'Near black, blue, or purple flowers', '4 - 19', '2,500'],
        ['Pill Bug', 'Mar - Dec', 'Hit rocks', '23 - 16', '250'],
        ['Pondskater', 'Nov - Mar', 'River', '8 - 19', '130'],
        ['Queen Alexandra’s Birdwing', 'Nov - Mar', 'Flying', '8 - 16', '4,000'],
        ['Rainbow Stag', 'Dec - Mar', 'Tree', '19 - 8', '6,000'],
        ['Rajah Brooke’s Birdwing', 'June - Aug | Oct - Mar', 'Near black, blue, or purple flowers', '8 - 17', '2,500'],
        ['Red Dragonfly', 'Mar - Apr', 'Flying', '8 - 19', '180'],
        ['Rosalia Batsei Beetle', 'Nov - Dec', 'Tree stump', 'All day', '3,000'],
        # ['Scorpion', 'TBD', 'Ground', 'Night', ''],
        ['Snail', 'All year', 'Rock (rain)', 'All day', '250'],
        ['Spider', 'All year', 'Shake tree', '19 - 8', '600'],
        ['Stinkbug', 'Sept - Apr', 'Flowers', 'All day', '120'],
        ['Tarantula', 'May - Oct', 'Ground', '19 - 4', '8,000'],
        ['Tiger Beetle', 'Aug - Apr', 'Ground', 'All day', '1,500'],
        ['Tiger Butterfly', 'Sept - Mar', 'Flying', '4 - 19', '240'],
        ['Violin Beetle', 'Mar - May | Nov - Dec', 'Tree stump', 'All day', '450'],
        ['Walker Cicada', 'Feb - Mar', 'Tree', '8 - 16', '400'],
        ['Walking Leaf', 'Jan - Mar', 'Ground', 'All day', '600'],
        ['Wasp', 'All year', 'Shake Tree', 'All day', '2,500'],
        ['Wharf Roach', 'All year', 'Beach (rocks)', 'All day', '200'],
        ['Yellow Butterfly', 'Mar - Apr | Sept - Dec', 'Flying', '4 - 19', '160']]

def load_dict():
    return {
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'June' : 6,
        'July' : 7,
        'Aug' : 8,
        'Sept' : 9,
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12
    }
