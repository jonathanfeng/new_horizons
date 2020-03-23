from datetime import datetime
import pytz
import csv

def main(tz, fish_list):
    active_fishies = process_fish(fish_list, datetime.now(pytz.timezone(tz)))
    for v in active_fishies:
        v[2] = f"{v[2]:,d}"
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
            fish_times = fish[3]
            if fish_times != 'All day':
                fish_times = fish_times.split(' - ')
                fish_times = fish_times[0] + ':00 - ' + fish_times[1] + ':00'
            good_fish.append([fish[0], fish[2], int(fish[4].replace(',','')), fish[1], fish_times])
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
                    if (month >= m1 and month <= 12) or (month <= m2 and month >= 1):
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
    return list(csv.reader(open('app/bin/northern_fishes.csv')))

def load_southern():
    return list(csv.reader(open('app/bin/southern_fishes.csv')))

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
