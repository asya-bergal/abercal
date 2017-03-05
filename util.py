from dateutil.parser import parse
from datetime import datetime, time
from functools import reduce
from tzlocal import get_localzone

DEBUG = True

def debug(s):
    if DEBUG:
        print(s)

class InputError(Exception):
    pass

# Dates are stored in the JSON file as timezone-aware datetimes.
# Timezones are converted if necessary when loaded into memory
def decode_date(date_str):
    stored_dt = parse(date_str)
    local_tz = get_localzone()
    return stored_dt.astimezone(tz=local_tz)

def local_now():
    local_tz = get_localzone()
    return local_tz.localize(datetime.now())

def local_time_max():
    res = time.max
    tzinfo = get_localzone()
    return res.replace(tzinfo=tzinfo)

def local_time_min():
    res = time.min
    tzinfo = get_localzone()
    return res.replace(tzinfo=tzinfo)
# Decorator that removes keyword arguments that are passed in with None
# TODO: I'm not convinced that this is actually working.
def drop_nones(f):
    def wrapper(*args, **old_kw):
        new_kw = {k:v for k,v in old_kw.items() if v}
        return f(*args, **new_kw)
    return wrapper

def stringify_datetimes(dts):
    return reduce(lambda x,y: x + (y.isoformat() + ", "), dts, "")

def stringify_dates(dts):
    return reduce(lambda x,y: x + (y.date().isoformat() + ", "), dts, "")

def date_in(dt, dts):
    return any([dt.date() == x.date() for x in dts])
