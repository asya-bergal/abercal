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
        # Returns the time of the event on a given date, or None if
        # the event doesn't occur on that date
        def time_on_date(self, dt):
            # Check if date is any of the starting datetimes
            for starting_date in self.starting_dates:
                if dt.date() == x.date():
                    return starting_date.time()
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
                        if dt.date() == cur_date.date():
                            return starting_date.time()
            return None

        def __str__(self):
            return '%s : %s%s%s' % (self.description,
                stringify_dates(self.starting_dates),
                " for " + duration.isoformat(),
                " at " + self.location if self.location else "",
                "\n" + str(self.repeater) if self.repeater else "")
