import parsedatetime
from datetime import *
from tzlocal import get_localzone
from pytimeparse.timeparse import timeparse

from util import *

# If you explicitly pass in a timezone, it will assume that,
# Otherwise it will use your local timezone.
def parse_datetime(datetime_str, relative_base):
    cal = parsedatetime.Calendar()

    dt, result_type = cal.parseDT(datetime_str, sourceTime = relative_base)

    # We parsed out a date, make it into a datetime
    if result_type == 1:
        dt = datetime.combine(dt, datetime.now().time())
    # We parsed out a time, make it into a datetime
    elif result_type == 0:
        raise InputError('Error: could not successfully convert \'%s\' to date and time.',
                             datetime_str)
    local_tz = get_localzone()
    dt = local_tz.localize(dt)
    return dt

def parse_timedelta(timedelta_str):
    seconds = timeparse(timedelta_str)
    if not seconds:
        raise InputError('Error: could not successfully convert \'%s\' to duration.',
                             timedelta_str)
    return timedelta(seconds=seconds)
