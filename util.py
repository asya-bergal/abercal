import dateparser
from tzlocal import get_localzone

class InputError(Exception):
    pass
# Dates are stored in the JSON file as timezone-aware datetimes.
# Timezones are converted if necessary when loaded into memory
def decode_date(date_str):
    stored_dt = dateparser.parse(date_str, settings = {'RETURN_AS_TIMEZONE_AWARE': True} )
    local_tz = get_localzone()
    return stored_dt.astimezone(tz=local_tz)

# Decorator that removes keyword arguments that are passed in with None
# TODO: I'm not convinced that this is actually working.
def drop_nones(f):
    def wrapper(*args, **old_kw):
        new_kw = {k:v for k,v in old_kw.items() if v}
        return f(*args, **new_kw)
    return wrapper

def stringify_dates(dts):
    return reduce(lambda x,y: x + (y.isoformat() + ", "), "", dts)
