from datetime import *
from enum import *
import json, argparse, dateparser, os.path, pytz
from tzlocal import get_localzone

# Decorator that removes keyword arguments that are passed in with None
def drop_nones(f):
    def wrapper(*args, **old_kw):
        new_kw = {k:v for k,v in old_kw.items() if v}
        return f(*args, **new_kw)
    return wrapper

# Convert unaware date-time object specified in your system's time zone
# to an unaware date-time object that's actually in UTC.
def utcify(dt):
    if dt:
        tz = get_localzone()
        local_dt = tz.localize(dt)
        return local_dt.astimezone(pytz.utc).replace(tzinfo=None)
    else:
        return None


class Event:
    def __init__(self, description, dt, location=""):
        self.description = description
        self.dt = dt
        self.location = location

    def __str__(self):
        return '%s : %s at %s' % (self.description, self.dt, self.location)

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task:

    def __init__(self, description, duedate = None, priority = Priority.LOW):
        self.description = description
        self.duedate = duedate
        self.priority = priority

    def __str__(self):
        return '%s due %s, priority %s' % (self.description, self.duedate, self.priority)

class CalendarEncoder(json.JSONEncoder):

    @staticmethod
    def encode_event(event):
        return {'description' : event.description,
                'dt' : event.dt.isoformat(),
                'location' : event.location}

    @staticmethod
    def encode_task(task):
        return {'description' : task.description,
                'duedate' : task.duedate.isoformat() if task.duedate else None,
                'priority' : task.priority}

    def default(self, obj):
        if isinstance(obj, Calendar):
            return {'name': obj.name,
                    'events' : [CalendarEncoder.encode_event(event) for event in obj.events],
                    'tasks' : [CalendarEncoder.encode_task(task) for task in obj.tasks]}
        else:
            return json.JSONEncoder.default(self, obj)

class CalendarDecoder(json.JSONDecoder):

    @staticmethod
    def decode_event(event):
        return Event(event['description'],
                     dateparser.parse(event['dt']),
                     event['location'])

    @staticmethod
    def decode_task(task):
        return Task(task['description'],
                     dateparser.parse(task['duedate']) if task['duedate'] else None,
                     task['priority'])

    def decode(self, obj):
        data = json.JSONDecoder.decode(self, obj)
        return {'events' : [CalendarDecoder.decode_event(event) for event in data['events']],
                'tasks' : [CalendarDecoder.decode_task(task) for task in data['tasks']]}

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

    def load(self):
        with open(self.fname, 'r') as f:
            data = json.load(f, cls=CalendarDecoder)
        self.events = data['events']
        self.tasks = data['tasks']

    def dump(self):
        with open(self.fname, 'w') as f:
            json.dump(self, f, cls=CalendarEncoder, indent=2)

    @drop_nones
    def add_event(self, description, datetime, location=""):
        self.events.append(Event(description, utcify(datetime), location))
        for event in self.events:
            print(event)
        self.events.sort(key=lambda event: (event.dt, event.description))
        self.dump()

    @drop_nones
    def add_task(self, description, duedate=None, priority=Priority.LOW):
        self.tasks.append(Task(description, utcify(duedate), priority))
        self.tasks.sort(key=lambda task: task.description)
        self.dump()

# - Add an event -e "description" -d "datetime" -l "location"
# - Add a task -t "description" -d "datetime" -p "priority"
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--calendar', required=True)
    parser.add_argument('-e','--event')
    parser.add_argument('-t','--task')
    parser.add_argument('-d','--datetime')
    parser.add_argument('-l','--location')
    parser.add_argument('-p','--priority')
    args = parser.parse_args()

    # TODO: Better error message
    calendar = Calendar(args.calendar)
    # Add an event
    if args.event:
        if args.datetime:
            parsed_date = dateparser.parse(args.datetime)
            if parsed_date:
                calendar.add_event(args.event, parsed_date, args.location)
            else:
                print("Failed to parse datetime string, try again.")
        else:
            print("An event must have an ending time, specified with [-d, --datetime].")
    # Add a task
    elif args.task:
        if args.datetime:
            parsed_date = dateparser.parse(args.datetime)
            if parsed_date:
                calendar.add_task(args.task, parsed_date, args.priority)
            else:
                print("Failed to parse datetime string, try again.")
        else:
            calendar.add_task(args.task, None, args.priority)

if __name__ == "__main__":
    main()
