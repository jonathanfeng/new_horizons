import pytz
from datetime import datetime, tzinfo
from pprint import pprint

def get_timezones():
    timezones = pytz.common_timezones
    tzs = []
    for timezone in timezones:
        tzs.append([timezone, datetime.now(pytz.timezone(timezone)).strftime('%z')])
    return tzs
