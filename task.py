from enum import *

from util import *
from repeater import Repeater

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task:

    def __init__(self,
                 description,
                 due_dates=[],
                 priority=Priority.LOW,
                 repeater=None,
                 completed = []):
        self.description = description
        self.due_dates = due_dates
        self.priority = priority
        self.repeater = repeater
        # Dates of this task that have been completed
        self.completed = completed

    def __str__(self):
        return '%s : %s%s%s%s' % (self.description,
                                  "Due " + stringify_dates(self.due_dates), 
                                  " priority %s" + duration.isoformat() if self.priority else "",
                                  "\n" + str(self.repeater) if self.repeater else "",
                                  "\nCompleted " + stringify_dates(self.completed))
