from datetime import datetime
import pytz
import csv
from pprint import pprint

def main(tz, creature_list):
    active_creatures = process_sea_creatures(creature_list, datetime.now(pytz.timezone(tz)))
    for v in active_creatures:
        if v[1] == 0:
            v[1] = '?'
        else:
            v[1] = f"{v[1]:,d}"
    return active_creatures

def process_sea_creatures(creature_list, dt):
    month = dt.month
    hour = dt.hour
    good_creatures = []
    for creature in creature_list:
        name = creature[0]
        price = creature[1]
        if price == '?':
            price = "0"
        shadow_size = creature[2]
        shadow_movement = creature[3]
        times = creature[4]
        seasonality = creature[5]
        good_month = test_seasonality(seasonality, month)
        good_time = test_time(times, hour)
        if good_month and good_time:
            creature_times = times
            if creature_times.lower() != 'all day':
                creature_times = clean_times(creature_times)
            seasonality = clean_months(seasonality)
            good_creatures.append([name, int(price.replace(',','')), shadow_size, shadow_movement, creature_times, seasonality])
    return sorted(good_creatures, key=lambda x:x[1],reverse=True)

def clean_times(creature_times):
    temp_times = creature_times.split(' & ')
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
                # Keep checking other time ranges if the first doesn't match
            else: # Overnight case
                if (hour >= t[0] and hour < 24) or (hour < t[1] and hour >= 0):
                    return True
        # If no time range matched after checking all
        return False


def load_northern():
    northern_creatures = list(csv.reader(open('app/bin/critterdb/northern_sea_creatures.csv')))
    new_n_creatures = []
    for creature in northern_creatures:
        months = []
        name = creature[0]
        price = creature[1]
        shadow_size = creature[2]
        shadow_movement = creature[3]
        times = creature[4]
        active_months = [m for m in creature[5:17]]
        inverse_month = inverse_months()
        i = 1
        for am in active_months:
            if am == "1":
                months.append(inverse_month[i])
            i += 1
        new_n_creatures.append([name, price, shadow_size, shadow_movement, times, months])
    return new_n_creatures

def load_southern():
    # Note: This loads northern data and shifts months.
    # You might need a southern_sea_creatures.csv if seasonality differs more complexly.
    northern_creatures = list(csv.reader(open('app/bin/critterdb/northern_sea_creatures.csv')))
    southern_creatures = []
    for creature in northern_creatures:
        months = []
        name = creature[0]
        price = creature[1]
        shadow_size = creature[2]
        shadow_movement = creature[3]
        times = creature[4]
        active_months = [m for m in creature[5:17]]
        inverse_month = inverse_months()
        i = 1
        for am in active_months:
            # Shift month index by 6 for Southern Hemisphere
            i2 = (i+6)%12
            # Use 12 for Dec instead of 0 from modulo
            if i2 == 0:
                i2 = 12
            if am == "1":
                months.append(inverse_month[i2])
            i += 1
        southern_creatures.append([name, price, shadow_size, shadow_movement, times, months])
    return southern_creatures


def load_dict():
    # Month name to number mapping
    return {
        'Jan' : 1,
        'Feb' : 2,
        'Mar' : 3,
        'Apr' : 4,
        'May' : 5,
        'Jun' : 6, # Corrected June spelling
        'Jul' : 7,
        'Aug' : 8,
        'Sep' : 9, # Corrected Sept spelling
        'Oct' : 10,
        'Nov' : 11,
        'Dec' : 12
    }

def inverse_months():
    # Month number to name mapping
    return {
        0 : 'Dec', # Handles modulo wrap-around case in Southern load
        1 : 'Jan',
        2 : 'Feb',
        3 : 'Mar',
        4 : 'Apr',
        5 : 'May',
        6 : 'Jun', # Corrected June spelling
        7 : 'Jul',
        8 : 'Aug',
        9 : 'Sep', # Corrected Sept spelling
        10 : 'Oct',
        11 : 'Nov',
        12 : 'Dec'
    }

if __name__ == "__main__":
    # Example usage for testing
    print("--- Northern Hemisphere ---")
    pprint(main('America/Los_Angeles', load_northern()))
    print("\n--- Southern Hemisphere ---")
    pprint(main('America/Los_Angeles', load_southern())) 