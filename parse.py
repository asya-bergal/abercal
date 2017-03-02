import dateparser
from datetime import *
from tzlocal import get_localzone
from pytimeparse.timeparse import timeparse

from util import *

# If you explicitly pass in a timezone, it will assume that,
# Otherwise it will use your local timezone.
def parse_datetime(datetime_str, relative_base):
    dt = dateparser.parse(datetime_str,
                            settings = {'RELATIVE_BASE': relative_base,
                                        'RETURN_AS_TIMEZONE_AWARE': True})
    # If no timezone is explicitly specified in the string, set it to use
    # your local timezone.
    if not dt:
        raise InputError('Error: could not successfully convert \'%s\' to date and time.',
                             datetime_str) 
    if not dt.tzinfo:
        local_tz = get_localzone()
        dt = local_tz.localize(dt)
    return dt

def parse_timedelta(timedelta_str):
    seconds = timeparse(timedelta_str)
    if not seconds:
        raise InputError('Error: could not successfully convert \'%s\' to duration.',
                             timedelta_str)
    return timedelta(seconds=seconds)
