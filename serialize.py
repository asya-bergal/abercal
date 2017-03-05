import json

from parse import *
from util import *
from repeater import Repeater
from event import Event
from task import Task, Priority
import cal

class CalendarEncoder(json.JSONEncoder):

    @staticmethod
    def encode_timedelta(timedelta):
        return str(timedelta)

    @staticmethod
    def encode_repeater(repeater):
        return {'days_delta' : repeater.days_delta,
                'exceptions' : [x.isoformat() for x in repeater.exceptions],
                'end_date' : repeater.end_date.isoformat() if repeater.end_date else None}

    @staticmethod
    def encode_event(event):
        return {'description' : event.description,
                'starting_dates' : [x.isoformat() for x in event.starting_dates],
                'duration' : CalendarEncoder.encode_timedelta(event.duration),
                'location' : event.location,
                'repeater' : CalendarEncoder.encode_repeater(event.repeater) if event.repeater else None}

    @staticmethod
    def encode_task(task):
        return {'description' : task.description,
                'due_dates' : [x.isoformat() for x in task.due_dates],
                'priority' : task.priority.name if task.priority else None,
                'repeater' : CalendarEncoder.encode_repeater(task.repeater) if task.repeater else None,
                'completed' : [x.isoformat() for x in task.completed]}

    def default(self, obj):
        if isinstance(obj, cal.Calendar):
            return {'name': obj.name,
                    'events' : [CalendarEncoder.encode_event(event) for event in obj.events],
                    'tasks' : [CalendarEncoder.encode_task(task) for task in obj.tasks]}
        else:
            return json.JSONEncoder.default(self, obj)

class CalendarDecoder(json.JSONDecoder):

    @staticmethod
    def decode_timedelta(td):
        return parse_timedelta(td)

    @staticmethod
    def decode_repeater(repeater):
        return Repeater(repeater['days_delta'],
                        list(map(decode_date, repeater['exceptions'])),
                        decode_date(repeater['end_date']) if repeater['end_date'] else None)

    @staticmethod
    def decode_event(event):
        return Event(event['description'],
                     list(map(decode_date, event['starting_dates'])),
                     CalendarDecoder.decode_timedelta(event['duration']),
                     event['location'],
                     CalendarDecoder.decode_repeater(event['repeater']) if event['repeater'] else None)

    @staticmethod
    def decode_task(task):
        return Task(task['description'],
                     list(map(decode_date, task['due_dates'])),
                     Priority[task['priority']] if task['priority'] else None,
                     CalendarDecoder.decode_repeater(task['repeater']) if task['repeater'] else None,
                     list(map(decode_date, task['completed'])))

    def decode(self, obj):
        data = json.JSONDecoder.decode(self, obj)
        return {'events' : [CalendarDecoder.decode_event(event) for event in data['events']],
                'tasks' : [CalendarDecoder.decode_task(task) for task in data['tasks']]}
