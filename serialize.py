import json

from parse import *
from util import *
from repeater import Repeater
from event import Event
from task import DueTask, PriorityTask, Priority
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
    def encode_due_task(task):
        return {'description' : task.description,
                'due_dates' : [x.isoformat() for x in task.due_dates],
                'repeater' : CalendarEncoder.encode_repeater(task.repeater) if task.repeater else None,
                'completed' : [x.isoformat() for x in task.completed]}

    @staticmethod
    def encode_priority_task(task):
        return {'description' : task.description,
                'priority' : task.priority.name,
                'completed' : task.completed}

    def default(self, obj):
        if isinstance(obj, cal.Calendar):
            return {'name': obj.name,
                    'events' : [CalendarEncoder.encode_event(event) for event in obj.events],
                    'due_tasks' : [CalendarEncoder.encode_due_task(task) for task in obj.due_tasks],
                    'priority_tasks':[CalendarEncoder.encode_priority_task(task) for task in obj.priority_tasks]}
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
    def decode_due_task(task):
        return DueTask(task['description'],
                       list(map(decode_date, task['due_dates'])),
                       CalendarDecoder.decode_repeater(task['repeater']) if task['repeater'] else None,
                       list(map(decode_date, task['completed'])))

    @staticmethod
    def decode_priority_task(task):
        return PriorityTask(task['description'],
                            Priority[task['priority']],
                            task['completed'])

    def decode(self, obj):
        data = json.JSONDecoder.decode(self, obj)
        return {'events' : [CalendarDecoder.decode_event(event) for event in data['events']],
                'due_tasks' : [CalendarDecoder.decode_due_task(task) for task in data['due_tasks']],
                'priority_tasks' : [CalendarDecoder.decode_priority_task(task) for task in data['priority_tasks']]}
