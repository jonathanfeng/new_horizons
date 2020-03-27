from datetime import datetime
import pytz
import csv
from pprint import pprint

def main(tz, fish_list):
    active_fishies = process_fish(fish_list, datetime.now(pytz.timezone(tz)))
    for v in active_fishies:
        if v[1] == 0:
            v[1] = '?'
        else:
            v[1] = f"{v[1]:,d}"
    return active_fishies

def process_fish(fish_list, dt):
    month = dt.month
    hour = dt.hour
    good_fish = []
    for fish in fish_list:
        name = fish[0]
        price = fish[1]
        if price == '?':
            price = "0"
        location = fish[2]
        shadow = fish[3]
        times = fish[4]
        seasonality = fish[5]
        good_month = test_seasonality(seasonality, month)
        good_time = test_time(times, hour)
        if good_month and good_time:
            fish_times = times
            if fish_times.lower() != 'all day':
                fish_times = clean_times(fish_times)
            seasonality = clean_months(seasonality)
            good_fish.append([name, int(price.replace(',','')), location, fish_times, seasonality, shadow])
    return sorted(good_fish, key=lambda x:x[1],reverse=True)

def clean_times(fish_times):
    temp_times = fish_times.split(' & ')
    return_times = ""
    for tim in temp_times:
        tim = tim.split(' - ')
        temp_time = []
        for t in tim:
            if int(t) > 12:
                temp_time.append(str(int(t)-12) + ' PM')
            else:
                temp_time.append(str(int(t)) + ' AM')
        temp_counter = 0
        for temp_t in temp_time:
            if temp_counter == 0:
                return_times += temp_t
            else:
                return_times += ' - ' + temp_t
            temp_counter += 1
        if tim != temp_times[-1] and len(temp_times) != 1:
            return_times += ', '
    return return_times

def clean_months(seasonality):
    if len(seasonality) == 12:
        return 'All year'
    else:
        ranges = []
        start = 0
        for i in range(0, len(seasonality)):
            if i == len(seasonality)-1 or seasonality[i+1] != nxt(seasonality[i]):
                # add months to output list
                ranges.append((seasonality[start], seasonality[i]))
                start = i+1
        if ranges[0][0] == 'Jan' and ranges[-1][1] == 'Dec':
            ranges[0] = (ranges[-1][0], ranges[0][1])
            ranges.pop()
        months = [range_str(rng) for rng in ranges]
        return ', '.join(months)

def range_str(rng):
    if rng[0] == rng[1]:
        return rng[0]
    return '{} - {}'.format(rng[0], rng[1])

def nxt(month):
    mos = list(load_dict().keys())
    return mos[(mos.index(month)+1)%len(mos)]

def test_seasonality(seasonality, month):
    inverses = inverse_months()
    if inverses[month] in seasonality:
        return True
    else:
        return False

def test_time(times, hour):
    if times == 'All day':
        return True
    else:
        times = times.split(' & ')
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
    northern_fish = list(csv.reader(open('app/bin/critterdb/northern_fishes.csv')))
    new_n_fish = []
    for fish in northern_fish:
        months = []
        name = fish[0]
        price = fish[1]
        location = fish[2]
        shadow = fish[3]
        times = fish[4]
        active_months = [m for m in fish[5:17]]
        inverse_month = inverse_months()
        i = 1
        for am in active_months:
            if am == "1":
                months.append(inverse_month[i])
            i += 1
        new_n_fish.append([name, price, location, shadow, times, months])
    return new_n_fish

def load_southern():
    northern_fish = list(csv.reader(open('app/bin/critterdb/northern_fishes.csv')))
    southern_fish = []
    for fish in northern_fish:
        months = []
        name = fish[0]
        price = fish[1]
        location = fish[2]
        shadow = fish[3]
        times = fish[4]
        active_months = [m for m in fish[5:17]]
        inverse_month = inverse_months()
        i = 1
        for am in active_months:
            i2 = (i+6)%12
            if am == "1":
                months.append(inverse_month[i2])
            i += 1
        southern_fish.append([name, price, location, shadow, times, months])
    return southern_fish

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

def inverse_months():
    return {
        0 : 'Dec',
        1 : 'Jan',
        2 : 'Feb', 
        3 : 'Mar', 
        4 : 'Apr',
        5 : 'May',
        6 : 'June',
        7 : 'July',
        8 : 'Aug',
        9 : 'Sept',
        10 : 'Oct',
        11 : 'Nov',
        12 : 'Dec'
    }

if __name__ == "__main__":
    pprint(main('America/Los_Angeles', load_northern()))
