from datetime import datetime
import pytz
import csv

def main(tz, bug_list):
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
            bug_times = bug[3]
            if bug_times != 'All day':
                bug_times = bug_times.split(' - ')
                bug_times = bug_times[0] + ':00 - ' + bug_times[1] + ':00'
            good_bug.append([bug[0], bug[2], int(bug[4].replace(',','')), bug[1], bug_times])
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
    return list(csv.reader(open('app/bin/northern_bugs.csv')))

def load_southern():
    return list(csv.reader(open('app/bin/southern_bugs.csv')))

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
