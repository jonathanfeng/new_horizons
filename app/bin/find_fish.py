from datetime import datetime
import pytz

def main(hemisphere, tz):
    if hemisphere == 'Northern':
        fish_list = load_northern()
    else:
        fish_list = load_southern()
    active_fishies = process_fish(fish_list, datetime.now(pytz.timezone(tz)))
    return active_fishies

def process_fish(fish_list, dt):
    month = dt.month
    hour = dt.hour
    good_fish = []
    for fish in fish_list:
        seasonality = fish[1]
        times = fish[3]
        good_month = test_seasonality(seasonality, month)
        good_time = test_time(times, hour)
        if good_month and good_time:
            if fish[3] != 'All day':
                fish_times = fish[3].split(' - ')
                fish[3] = fish_times[0] + ':00 - ' + fish_times[1] + ':00'
            good_fish.append([fish[0], fish[2], int(fish[4].replace(',','')), fish[1], fish[3]])
    return sorted(good_fish, key=lambda x:x[2],reverse=True)
     
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
        ['Anchovy', 'All year', 'Ocean', '4 - 21', '200'],
        ['Angelfish', 'May - Oct', 'River', '16 - 9', '3,000'],
        ['Arowana', 'June - Sept', 'River', '16 - 9', '10,000'],
        ['Barred Knifejaw', 'Mar - Nov', 'Ocean', 'All day', '5,000'],
        ['Barreleye', 'All year', 'Ocean', '21 - 4', '12,000'],
        ['Betta', 'May - Oct', 'River', '9 - 16', '2,500'],
        ['Bitterling', 'Nov - Mar', 'River', 'All day', '900'],
        ['Black Bass', 'All year', 'River', 'All day', '400'],
        ['Blowfish', 'Nov - Feb', 'Ocean', '21 - 4', '5,000'],
        ['Blue Marlin', 'Nov - Apr | July - Sept', 'Pier', 'All day', '10,000'],
        ['Bluegill', 'All year', 'River', '9 - 16', '180'],
        ['Carp', 'All year', 'River', 'All day', '300'],
        ['Catfish', 'May - Oct', 'Pond', '16 - 9', '800'],
        ['Char', 'Mar - June | Sept - Nov', 'River', '16 - 9', '3,800'],
        ['Cherry Salmon', 'Mar - June | Sept - Nov', 'River (Clifftop)', 'All day', '1,000'],
        ['Clownfish', 'Apr - Sept', 'Ocean', 'All day', '650'],
        ['Coelacanth', 'All year', 'Ocean (Rain)', 'All day', '15,000'],
        ['Crawfish', 'Apr - Sept', 'Pond', 'All day', '200'],
        ['Crucian Carp', 'All year', 'River', 'All day', '160'],
        ['Dab', 'Oct - Apr', 'Ocean', 'All day', '300'],
        ['Dace', 'All year', 'River', '16 - 9', '240'],
        ['Football Fish', 'Nov - Mar', 'Ocean', '16 - 9', '2,500'],
        ['Freshwater Goby', 'All year', 'River', '16 - 9', '400'],
        ['Golden Trout', 'Mar - May | Sept - Nov', 'River (Clifftop)', '16 - 9','15,000'],
        ['Goldfish', 'All year', 'Pond', 'All day', '1,300'],
        ['Guppy', 'Apr - Nov', 'River', '9 - 16', '1,300'],
        ['Hammerhead Shark', 'June - Sept', 'Ocean', '16 - 9', '8,000'],
        ['Horse Mackerel', 'All year', 'Ocean', 'All day', '150'],
        ['King Salmon', 'Sept', 'River (Mouth)', 'All day', '1,800'],
        ['Koi', 'All year', 'Pond', '16 - 9', '4,000'],
        ['Loach', 'Mar - May', 'River', 'All day', '400'],
        ['Mitten Crab', 'Sept - Nov', 'River', '16 - 9', '2,000'],
        ['Moray Eel', 'Aug - Oct', 'Ocean', 'All day', '2,000'],
        ['Neon Tetra', 'Apr - Nov', 'River', '4 - 16', '500'],
        ['Oarfish', 'Dec - May', 'Ocean', 'All day', '9,000'],
        ['Ocean Sunfish', 'July - Sept', 'Ocean', '4 - 21', '4,000'],
        ['Olive Flounder', 'All year', 'Ocean', 'All day', '800'],
        ['Pale Chub', 'All year', 'River', '9 - 16', '200'],
        ['Pike', 'Sept - Dec', 'River', 'All day', '1,800'],
        ['Piranha', 'June - Sept', 'River', '9 - 16 | 4 - 21', '2,500'],
        ['Pond Smelt', 'Dec - Feb', 'River', 'All day', '320'],
        ['Pop-eyed Goldfish', 'All year', 'Pond', '9 - 16', '1,300'],
        ['Puffer Fish', 'July - Sept', 'Ocean', 'All day', '250'],
        ['Rainbowfish', 'May - Oct', 'River', '9 - 16', '800'],
        ['Ranchu Goldfish', 'All year', 'Pond', '9 - 16', '4,500'],
        ['Ray', 'Aug - Nov', 'Ocean', '4 - 21', '3,000'],
        ['Red Snapper', 'All year', 'Ocean', 'All day', '3,000'],
        ['Ribbon Eel', 'July - Oct', 'Ocean', 'All day', '600'],
        ['Salmon', 'Sept', 'River (Mouth)', 'All day', '700'],
        ['Sea Bass', 'All year', 'Ocean', 'All day', '400'],
        ['Sea Butterfly', 'Dec - Mar', 'Ocean', 'All day', '1,000'],
        ['Seahorse', 'Apr - Nov', 'Ocean', 'All day', '1,100'],
        ['Soft-shelled Turtle', 'Aug - Sept', 'River', '16 - 9', '3,750'],
        ['Squid', 'Dec - Aug', 'Ocean', 'All day', '500'],
        ['Stringfish', 'Dec - Mar', 'River (Clifftop)', '16 - 9', '15,000'],
        ['Sturgeon', 'Sept - Mar', 'River (Mouth)', 'All day', '10,000'],
        ['Suckerfish', 'June - Sept', 'Ocean', 'All day', '1,500'],
        ['Sweetfish', 'July - Sept', 'River', 'All day', '900'],
        ['Tadpole', 'Mar - July', 'Pond', 'All day', '100'],
        ['Tilapia', 'June - Oct', 'River', 'All day', '800'],
        ['Tuna', 'Nov - Apr', 'Pier', 'All day', '7,000'],
        ['Whale Shark', 'June - Sept', 'Ocean', 'All day', '13,000'],
        ['Yellow Perch', 'Oct - Mar', 'River', 'All day', '300'],
        ['Zebra Turkeyfish', 'Apr - May | July - Nov', 'Ocean', 'All day', '500']]

def load_southern():
    return [
        ['Anchovy', 'All year', 'Ocean', '4 - 21', '200'],
        ['Angelfish', 'Nov - Apr', 'River', '16 - 9', '3,000'],
        ['Arowana', 'Dec - Mar', 'River', '16 - 9', '10,000'],
        ['Barred Knifejaw', 'Sept - May', 'Ocean', 'All day', '5,000'],
        ['Barreleye', 'All year', 'Ocean', '21 - 4', '12,000'],
        ['Betta', 'Nov - Apr', 'River', '9 - 16', '2,500'],
        ['Bitterling', 'May - Sept', 'River', 'All day', '900'],
        ['Black Bass', 'All year', 'River', 'All day', '400'],
        ['Blowfish', 'May - Aug', 'Ocean', '21 - 4', '5,000'],
        ['Blue Marlin', 'Jan - Mar | May - Oct', 'Pier', 'All day', '10,000'],
        ['Bluegill', 'All year', 'River', '9 - 16', '180'],
        ['Carp', 'All year', 'River', 'All day', '300'],
        ['Catfish', 'Nov - Apr', 'Pond', '16 - 9', '800'],
        ['Char', 'Mar - May | Sept - Dec', 'River', '16 - 9', '3,800'],
        ['Cherry Salmon', 'Mar - May | Sept - Dec', 'River (Clifftop)', 'All day', '1,000'],
        ['Clownfish', 'Oct - Mar', 'Ocean', 'All day', '650'],
        ['Coelacanth', 'All year', 'Ocean (Rain)', 'All day', '15,000'],
        ['Crawfish', 'Oct - Mar', 'Pond', 'All day', '200'],
        ['Crucian Carp', 'All year', 'River', 'All day', '160'],
        ['Dab', 'Apr - Oct', 'Ocean', 'All day', '300'],
        ['Dace', 'All year', 'River', '16 - 9', '240'],
        ['Football Fish', 'May - Sept', 'Ocean', '16 - 9', '2,500'],
        ['Freshwater Goby', 'All year', 'River', '16 - 9', '400'],
        ['Golden Trout', 'Mar - May, Sept - Nov', 'River (Clifftop)', '16 - 9', '15,000'],
        ['Goldfish', 'All year', 'Pond', 'All day', '1,300'],
        ['Guppy', 'Oct - May', 'River', '9 - 16', '1,300'],
        ['Hammerhead Shark', 'Dec - Mar', 'Ocean', '16 - 9', '8,000'],
        ['Horse Mackerel', 'All year', 'Ocean', 'All day', '150'],
        ['King Salmon', 'Mar', 'River (Mouth)', 'All day', '1,800'],
        ['Koi', 'All year', 'Pond', '16 - 9', '4,000'],
        ['Loach', 'Sept - Nov', 'River', 'All day', '400'],
        ['Mitten Crab', 'Mar - May', 'River', '16 - 9', '2,000'],
        ['Moray Eel', 'Feb - Apr', 'Ocean', 'All day', '2,000'],
        ['Neon Tetra', 'Oct - May', 'River', '4 - 16', '500'],
        ['Oarfish', 'June - Nov', 'Ocean', 'All day', '9,000'],
        ['Ocean Sunfish', 'Jan - Mar', 'Ocean', '4 - 21', '4,000'],
        ['Olive Flounder', 'All year', 'Ocean', 'All day', '800'],
        ['Pale Chub', 'All year', 'River', '9 - 16', '200'],
        ['Pike', 'Mar - June', 'River', 'All day', '1,800'],
        ['Piranha', 'Dec - Mar', 'River', '9 - 16 | 4 - 21', '2,500'],
        ['Pond Smelt', 'June - Aug', 'River', 'All day', '320'],
        ['Pop-eyed Goldfish', 'All year', 'Pond', '9 - 16', '1,300'],
        ['Puffer Fish', 'Jan - Mar', 'Ocean', 'All day', '250'],
        ['Rainbowfish', 'Nov - Apr', 'River', '9 - 16', '800'],
        ['Ranchu Goldfish', 'All year', 'Pond', '9 - 16', '4,500'],
        ['Ray', 'Feb - May', 'Ocean', '4 - 21', '3,000'],
        ['Red Snapper', 'All year', 'Ocean', 'All day', '3,000'],
        ['Ribbon Eel', 'Jan - Apr', 'Ocean', 'All day', '600'],
        ['Salmon', 'Mar', 'River (Mouth)', 'All day', '700'],
        ['Sea Bass', 'All year', 'Ocean', 'All day', '400'],
        ['Sea Butterfly', 'June - Sept', 'Ocean', 'All day', '1,000'],
        ['Seahorse', 'Oct - May', 'Ocean', 'All day', '1,100'],
        ['Soft-shelled Turtle', 'Feb - Mar', 'River', '16 - 9', '3,750'],
        ['Squid', 'June - Feb', 'Ocean', 'All day', '500'],
        ['Stringfish', 'June - Sept', 'River (Clifftop)', '16 - 9', '15,000'],
        ['Sturgeon', 'Mar - Sept', 'River (Mouth)', 'All day', '10,000'],
        ['Suckerfish', 'Dec - Mar', 'Ocean', 'All day', '1,500'],
        ['Sweetfish', 'Jan - Mar', 'River', 'All day', '900'],
        ['Tadpole', 'Sept - Jan', 'Pond', 'All day', '100'],
        ['Tilapia', 'Dec - Apr', 'River', 'All day', '800'],
        ['Tuna', 'May - Oct', 'Pier', 'All day', '7,000'],
        ['Whale Shark', 'Dec - Mar', 'Ocean', 'All day', '13,000'],
        ['Yellow Perch', 'Apr - Sept', 'River', 'All day', '300'],
        ['Zebra Turkeyfish', 'Jan - May | Oct - Nov', 'Ocean', 'All day', '500']]

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
