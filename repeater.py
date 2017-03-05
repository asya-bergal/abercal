from util import *

class Repeater:
    def __init__(self, days_delta, exceptions=[], end_date=None):
        self.days_delta = days_delta
        self.exceptions = exceptions
        self.end_date = end_date

        if self.days_delta == 0:
            raise InputError("Error: cannot have repeater that repeats every 0 days.")

    def __str__(self):
        return 'Repeats every %d days%s%s' % (self.days_delta,
                 (" except for " + stringify_dates(self.exceptions)) if self.exceptions else "",
                 " until " + self.end_date.date().isoformat() if self.end_date else "")
