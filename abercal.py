from datetime import *
from enum import *
import json, argparse, dateparser, os.path, pytz
from tzlocal import get_localzone
from pytimeparse.timeparse import timeparse

def parse_time(time_str):
    parts = regex.match(time_str)
    if not parts:
        return
    parts = parts.groupdict()
    time_params = {}
    for (name, param) in list(parts.items()):
        if param:
            time_params[name] = int(param)
    return timedelta(**time_params)

# Decorator that removes keyword arguments that are passed in with None
# TODO: I'm not convinced that this is actually working.
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

def stringify_dates(dts):
    return reduce(lambda x,y: x + (y.isoformat() + ", "), "", dts)

class Repeater:
    def __init__(self, days_delta, exceptions=[], end_date=None):
        self.days_delta = days_delta
        self.exceptions = exceptions
        self.end_date = end_date

    def __str__(self):
        return 'Repeats every %d days%s%s' % (self.days_delta,
                 " except for " + stringify_dates(dts) if self.exceptions else "",
                 " until " + self.end_date.isoformat() if self.end_date else "")

class Event:
    def __init__(self,
                 description,
                 datetimes,
                 duration=timedelta(hours=1),
                 location=None,
                 repeater=None):
        self.description = description
        self.datetimes = datetimes
        self.duration = duration
        self.location = location
        self.repeater = repeater

    def __str__(self):
        return '%s : %s%s%s' % (self.description,
             stringify_dates(self.datetimes),
             " for " + duration.isoformat(),
             " at " + self.location if self.location else "",
             "\n" + str(self.repeater) if self.repeater else "")

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class Task:

    def __init__(self,
                 description,
                 datetimes=[],
                 priority=Priority.LOW,
                 repeater=None,
                 completed = []):
        self.description = description
        self.datetimes = datetimes
        self.priority = priority
        self.repeater = repeater
        # Dates of this task that have been completed
        self.completed = completed

    def __str__(self):
        return '%s : %s%s%s%s' % (self.description,
                                  "Due " + stringify_dates(self.datetimes), 
                                  " priority %s" + duration.isoformat() if self.priority else "",
                                  "\n" + str(self.repeater) if self.repeater else "",
                                  "\nCompleted " + stringify_dates(self.completed))

class CalendarEncoder(json.JSONEncoder):

    # lol no one needs more than seconds of precision
    @staticmethod
    def encode_timedelta(timedelta):
        return {'days' : timedelta.days,
                'seconds' : timedelta.seconds}

    @staticmethod
    def encode_repeater(repeater):
        return {'days_delta' : repeater.days_delta,
                'exceptions' : [x.isoformat() for x in repeater.exceptions],
                'end_date' : repeater.end_date.isoformat() if repeater.end_date else None}

    @staticmethod
    def encode_event(event):
        return {'description' : event.description,
                'datetimes' : [x.isoformat() for x in event.datetimes],
                'duration' : CalendarEncoder.encode_timedelta(event.duration),
                'location' : event.location,
                'repeater' : CalendarEncoder.encode_repeater(event.repeater) if event.repeater else None}

    @staticmethod
    def encode_task(task):
        return {'description' : task.description,
                'datetimes' : [x.isoformat() for x in task.datetimes],
                'priority' : task.priority.name,
                'repeater' : CalendarEncoder.encode_repeater(task.repeater) if task.repeater else None,
                'completed' : [x.isoformat() for x in task.completed]}

    def default(self, obj):
        if isinstance(obj, Calendar):
            return {'name': obj.name,
                    'events' : [CalendarEncoder.encode_event(event) for event in obj.events],
                    'tasks' : [CalendarEncoder.encode_task(task) for task in obj.tasks]}
        else:
            return json.JSONEncoder.default(self, obj)

class CalendarDecoder(json.JSONDecoder):

    @staticmethod
    def decode_timedelta(td):
        return timedelta(days=td['days'], seconds=td['seconds'])

    @staticmethod
    def decode_repeater(repeater):
        return Repeater(repeater['days_delta'],
                        parse_datetimes(repeater['exceptions']),
                         dateparser.parse(repeater['end_date']))

    @staticmethod
    def decode_event(event):
        return Event(event['description'],
                     parse_datetimes(event['datetimes']),
                     CalendarDecoder.decode_timedelta(event['duration']),
                     event['location'],
                     decode_repeater(event['repeater']) if event['repeater'] else None)

    @staticmethod
    def decode_task(task):
        return Task(task['description'],
                     parse_datetimes(task['datetimes']),
                     Priority[task['priority']],
                     CalendarDecoder.decode_repeater(task['repeater']) if task['repeater'] else None,
                     parse_datetimes(task['completed']))

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
    def add_event(self,
                  description,
                  datetimes,
                  duration=timedelta(hours=1),
                  location=None,
                  days_delta=0,
                  exceptions=[],
                  enddate=None):
        self.events.append(Event(description,
                                 [utcify(dt) for dt in datetimes],
                                 timedelta(seconds=duration),
                                 location,
                                 Repeater(days_delta,
                                          [utcify(ex) for ex in exceptions],
                                          utcify(enddate)) if days_delta else None))
        self.events.sort(key=lambda event: (event.datetimes[0], event.description))
        self.dump()

    @drop_nones
    def add_task(self,
                 description,
                 datetimes=[],
                 priority=Priority.LOW,
                 days_delta=0,
                 exceptions=[],
                 enddate=None):
        self.tasks.append(Task(description,
                               [utcify(dt) for dt in datetimes],
                               priority,
                               Repeater(days_delta,
                                        [utcify(ex) for ex in exceptions],
                                        utcify(enddate)) if days_delta else None,
                               []))
        self.tasks.sort(key=lambda task: task.description)
        self.dump()

def parse_datetimes(datetimes, sttgs = {}):
    parsed_dts=[]
    for dt in datetimes:
        parsed_dt = dateparser.parse(dt, settings = sttgs)
        if not parsed_dt:
            return None
        parsed_dts.append(parsed_dt)
    return parsed_dts

# - Add an event -e "description" -l "location" -d "datetimes" -r "days-delta" -e "exceptions" -u "enddate"
# - Add an event -t "description" -l "priority" -d "datetimes" -r "days-delta" -e "exceptions" -u "enddate"
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--calendar', required=True)

    parser.add_argument('-e','--event')
    parser.add_argument('-t','--task')
    parser.add_argument('-dt','--datetimes', nargs='+')
    parser.add_argument('-d','--duration')
    parser.add_argument('-l','--location')
    parser.add_argument('-p','--priority')
    parser.add_argument('-r','--days-delta')
    parser.add_argument('-ex','--exceptions', nargs='+')
    parser.add_argument('-u','--enddate')

    args = parser.parse_args()

    # Record timestamp to produce consistent output with respect to dateparser
    timestamp = datetime.now()

    # TODO: Better error messages
    calendar = Calendar(args.calendar)

    parsed_datetimes = []
    parsed_exceptions = []
    parsed_duration = None
    parsed_enddate = None

    # Make sure original dates are parsed successfully
    if args.datetimes:
        parsed_datetimes=parse_datetimes(args.datetimes, sttgs={'RELATIVE_BASE': timestamp})
        if not parsed_datetimes:
            print("Failed to parse one or more datetime strings, try again.")
            return
    # Make sure duration string is parsed successfully
    if args.duration:
        parsed_duration=timeparse(args.duration)
        if not parsed_duration:
            print("Failed to parse event duration string, try again.")
            return
    # If the event is repeating, make sure the exception dates and enddate
    # is parsed successfully
    if args.exceptions:
        parsed_exceptions=parse_datetimes(args.exceptions, sttgs={'RELATIVE_BASE': timestamp})
        if not parsed_exceptions:
            print("Failed to parse one or more datetime strings, try again.")
            return
    if args.enddate:
        parsed_enddate = dateparser.parse(args.enddate, settings={'RELATIVE_BASE': timestamp})
        if not parsed_enddate:
            print("Failed to parse enddate string, try again.")
            return

    # Add an event
    if args.event:
        if parsed_datetimes:
            calendar.add_event(args.event,
                               parsed_datetimes,
                               duration=parsed_duration,
                               location=args.location,
                               days_delta=int(args.days_delta) if args.days_delta else None,
                               exceptions=parsed_exceptions,
                               enddate=parsed_enddate)
        else:
            print("An event must have one or more datetimes, specified with [-d, --datetimes].")
    # Add a task
    elif args.task:
        calendar.add_task(args.task,
                          datetimes=parsed_datetimes,
                          priority=args.priority,
                          days_delta=int(args.days_delta) if args.days_delta else None,
                          exceptions=parsed_exceptions,
                          enddate=parsed_enddate)

if __name__ == "__main__":
    main()
