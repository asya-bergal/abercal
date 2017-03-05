import copy
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

    # Check if an event scheduled on dt going from start_time to end_time is currently happening.
    # Returns 0 if currently ongoing, -1 if it's already passed, 1 if it's upcoming
    def check_current(start_date, end_date):
        now = local_now()
        if start_date > now:
            return 1
        if end_date < now:
            return -1
        else:
            return 0

    # Given an interval specified by start and end datetime, compute the portion of the
    # interval that is on that date (could be None, or the entire day)
    @staticmethod
    def check_interval(dt, start_date, end_date):
        # Date is same day as event start
        if dt.date() == start_date.date():
            return (start_date.timetz(),
                    end_date.timetz() if end_date.date() == start_date.date()
                    else local_time_max())
        # Date is after event start
        elif dt.date() > start_date.date():
            # And before event end
            if dt.date() < end_date.date():
                return (local_time_min(), local_time_max())
            elif dt.date() == end_date.date() and end_date > dt:
                return (local_time_min(), end_date.timetz())
        return None

    # Return the portion of the event happening on that day
    # as an interval (start_time, end_time), or return None if none of the
    # event happens on that day
    def time_interval_on_date(self, dt):
        # Check if date is any of the starting datetime intervals
        for start_date in self.starting_dates:
            time_interval = Event.check_interval(dt, start_date, start_date+self.duration)
            if time_interval:
                return time_interval
        # Check if the date is encoded by the repeater.
        if self.repeater:
            # Check to make sure date is not in list of exceptions
            if date_in(dt, self.repeater.exceptions):
                return None
            # Check to make sure date is not past the end_date of the repeater
            if not self.repeater.end_date == None and dt.date() > self.repeater.end_date.date():
                return None
            for starting_date in self.starting_dates:
                cur_date = copy.deepcopy(starting_date)
                # Check multiples of days_delta up to the current date
                while cur_date < dt:
                    cur_date += timedelta(days=self.repeater.days_delta)
                    time_interval = Event.check_interval(dt, cur_date, cur_date+self.duration)
                    if time_interval:
                        return time_interval
        return None

    @staticmethod
    def schedule_str(start_time, end_time, description, location):
        return "%s - %s | %s%s" % (start_time.strftime("%H:%M"),
                                   end_time.strftime("%H:%M"),
                                   description,
                                   (" at " + location) if location else "")

    def __str__(self):
        return '%s : %s%s%s%s' % (self.description,
            stringify_dates(self.starting_dates),
            " for " + str(self.duration),
            (" at " + self.location) if self.location else "",
            ("\n" + str(self.repeater)) if self.repeater else "")
