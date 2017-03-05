import copy
from datetime import datetime, timedelta
from enum import *

from util import *
from repeater import Repeater

class DueTask():
    def __init__(self,
                 description,
                 due_dates,
                 repeater=None,
                 completed=[]):
        self.description = description
        self.due_dates = due_dates
        self.repeater = repeater
        # Dates of this task that have been completed
        self.completed = completed

        if not self.due_dates:
            raise InputError("Error: a due-date task must be initialized with one or more due dates.")

    def next_due_date(self, dt):
        for due_date in sorted(self.due_dates):
            if due_date > dt and not date_in(due_date, self.completed):
                return due_date
        return None

    # Return the time a task is due on a given date, or None if the task isn't due on that date
    # Structured a lot like time_interval_on_date in Event.py
    def time_due_on_date(self, dt):
        # Check if date is in any of the starting due dates
        for due_date in self.due_dates:
            if due_date.date() == dt.date():
                return due_date.timetz()
        # Check if the date is encoded by the repeater
        if self.repeater:
            # Check to make sure date is not in list of exceptions
            if date_in(dt, self.repeater.exceptions):
                return None
            # Check to make sure date is not past the end_date of the repeater
            if not self.repeater.end_date == None and dt.date() > self.repeater.end_date.date():
                return None
            for due_date in self.due_dates:
                cur_date = copy.deepcopy(due_date)
                # Check multiples of days_delta up to the current date
                while cur_date < dt:
                    cur_date += timedelta(days=self.repeater.days_delta)
                    if cur_date.date() == dt.date():
                        return cur_date.timetz()
        return None

    @staticmethod
    def time_str(time, description):
        return "%s | %s" % (time.strftime("%H:%M"), description)

    def datetime_str(dt, description):
        return "%s | %s" % (dt.strftime("%m/%d %H:%M"), description)

    def __str__(self):
        return '   %s\n   %s%s%s' % (self.description,
                                               "Due: %s" % stringify_datetimes(self.due_dates),
                                               "\n   " + str(self.repeater) if self.repeater else "",
                                               "\n   Completed: %s" % stringify_dates(self.completed))

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class PriorityTask():
    def __init__(self,
                 description,
                 priority=Priority.LOW,
                 completed = False):

        self.description = description
        self.priority = priority
        # Has this task been completed? boolean
        self.completed = completed

    def __str__(self):
        return '   %s\n   %s\n   %s' % (self.description,
                                        "Priority: %s" % self.priority.name,
                                        "Completed: %s" % self.completed)
