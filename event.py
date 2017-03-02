from datetime import *

from util import *
from repeater import Repeater

class Event:
    def __init__(self,
                 description,
                 starting_dates,
                 duration=timedelta(hours=1),
                 location=None,
                 repeater=None):
        self.description = description
        self.starting_dates = starting_dates
        self.duration = duration
        self.location = location
        self.repeater = repeater

        if not self.starting_dates:
            raise InputError("Error: an event must be initialized with one or more starting dates.")

        if self.repeater and self.duration >= timedelta(days=1):
            raise InputError("Error: repeating events cannot last for more than a day.")

        # Check a single event interval, and compute the start and end time of the event
        # on the given time, or None if that event doesn't happen on that day.
        def check_interval(self, dt, start_date, end_date):
            if dt.date() == start_date.date():
                return (starting_date.time(),
                        end_date.time() if end_date.date() == starting_date.date()
                        else time.max)
            elif dt.date() > start_date.date():
                if dt.date() < end_date.date():
                    return (time.min, time.max)
                elif dt.date() == end_date.date():
                    return (time.min, end_date.time())
            return None

        def time_interval_on_date(self, dt):
            # Check if date is any of the starting datetime intervals
            for start_date in self.starting_dates:
                time_interval = check_interval(start_date, start_date+self.duration)
                if time_interval:
                    return time_interval
            # Check if the date is encoded by the repeater.
            if self.repeater:
                # Check to make sure date is not in list of exceptions
                if dt.date() in [x.date() for x in self.exceptions]:
                    return None
                # Check to make sure date is not past the end_date of the repeater
                if dt.date() > self.end_date.date():
                    return None
                for starting_date in self.starting_dates:
                    cur_date = copy.deepcopy(start_date)
                    # Check multiples of days_delta up to the current date
                    while cur_date < dt:
                        time_interval = check_interval(cur_date, cur_date+self.duration)
                        if time_interval:
                            return time_interval
            return None

        def __str__(self):
            return '%s : %s%s%s' % (self.description,
                stringify_dates(self.starting_dates),
                " for " + duration.isoformat(),
                " at " + self.location if self.location else "",
                "\n" + str(self.repeater) if self.repeater else "")
