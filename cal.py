from datetime import *
import json
import os.path

from util import *
import serialize

from repeater import Repeater
from event import Event
from task import Task, Priority

class Calendar:

    # TODO: Initialize calendar by importing file
    def __init__(self, name="mycal"):
        self.name = name
        self.fname = name + ".json"

        if os.path.isfile(self.fname):
            # Load existing calendar
            self.load()
        else:
            # Create new calendar
            self.events = []
            self.tasks = []
            self.dump()

    def ordered_daily_events(self, dt):
        events = filter(time_on_date, self.events)
        events.sort(key=time_on_date)

    def load(self):
        with open(self.fname, 'r') as f:
            data = json.load(f, cls=serialize.CalendarDecoder)
        self.events = data['events']
        self.tasks = data['tasks']

    def dump(self):
        with open(self.fname, 'w') as f:
            json.dump(self, f, cls=serialize.CalendarEncoder, indent=2)

    @drop_nones
    def add_event(self,
                  description,
                  starting_dates,
                  duration=timedelta(hours=1),
                  location=None,
                  days_delta=0,
                  exceptions=[],
                  enddate=None):
        self.events.append(Event(description,
                                 starting_dates,
                                 duration,
                                 location,
                                 Repeater(days_delta,
                                          exceptions,
                                          enddate) if days_delta else None))
        self.events.sort(key=lambda event: (event.starting_dates[0], event.duration))
        self.dump()

    @drop_nones
    def add_task(self,
                 description,
                 due_dates=[],
                 priority=Priority.LOW,
                 days_delta=0,
                 exceptions=[],
                 enddate=None):
        self.tasks.append(Task(description,
                               due_dates,
                               priority,
                               Repeater(days_delta,
                                        exceptions,
                                        enddate),
                               []))
        self.tasks.sort(key=lambda task: task.description)
        self.dump()
