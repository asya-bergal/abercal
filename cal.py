from datetime import *
import json
import os.path
from colorama import Fore, Back, Style

from util import *
import serialize

from repeater import Repeater
from event import Event
from task import DueTask, PriorityTask, Priority

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
            self.due_tasks = []
            self.priority_tasks = []
            self.dump()

    def ordered_daily_events(self, dt):
        events = list(filter(lambda x : x.time_interval_on_date(dt), self.events))
        events.sort(key=lambda x : x.time_interval_on_date(dt))
        return events

    def display_daily_schedule(self, dt):
        now = local_now()
        events = self.ordered_daily_events(dt)

        day_style = ""
        if dt.date() == now.date():
            day_style = Style.BRIGHT
        elif dt.date() < now.date():
            day_style = Style.DIM
        print(day_style + dt.strftime('%a, %d %b') + Style.RESET_ALL)
        # Print every event
        next_event_found = False
        for event in events:
            start_time, end_time = event.time_interval_on_date(dt)
            assert start_time
            assert end_time
            start_date = datetime.combine(dt.date(), start_time)
            end_date = datetime.combine(dt.date(), end_time)

            event_style = ""
            indent = "   "
            # Print any ongoing events brightly and use a carat to indicate
            # Current place in the schedule
            if start_date <= now and end_date >= now:
                event_style = Style.BRIGHT
                indent = " > "
                next_event_found = True
            # Print any past events dimly
            elif end_date < now:
                event_style = Style.DIM
            # If there's no ongoing event today, place the carat and brighten the
            # next upcoming event today
            elif dt.date() == now.date() and start_date > now and not next_event_found:
                event_style = Style.BRIGHT
                indent = " > "
                next_event_found = True

            # Actually print the schedule and reset the style afterwards
            print(event_style + indent +
                  Event.schedule_str(start_time, end_time,
                                     event.description, event.location) +
                  Style.RESET_ALL)

    def display_weekly_schedule(self, dt):
        week_start = dt - timedelta(days=((dt.weekday() + 1) % 7))
        # Display all 7 days in a week
        for day in range(7):
            self.display_daily_schedule(week_start + timedelta(days=day))
            if day==6:
                print("")

    def get_tasks_with_priority(self, priority):
        return list(filter(lambda x: x.priority == priority, self.priority_tasks))

    def ordered_daily_tasks(self, dt):
        # Check to make sure the task is due today, is not in the list of exceptions
        # if there's a repeater, and is not completed
        tasks_due_soon = list(filter(lambda task: task.time_due_on_date(dt) and
                                                  (not date_in(dt, task.repeater.exceptions)
                                                   if task.repeater else True) and
                                                  not date_in(dt, task.completed),
                                     self.due_tasks))
        tasks_due_soon.sort(key=lambda task: task.time_due_on_date(dt))
        return tasks_due_soon

    def display_daily_tasks(self, dt):
        tasks = self.ordered_daily_tasks(dt)

        for task in tasks:
            due_time = task.time_due_on_date(dt)
            assert due_time
            print("   " + DueTask.time_str(due_time, task.description))

    def display_weekly_tasks(self, dt):
        week_start = dt - timedelta(days=((dt.weekday() + 1) % 7))

        for day in range(7):
            cur_day = week_start + timedelta(days=day)

            fore = ""
            # Color the days corresponding to today and tomorrow red
            tomorrow = dt + timedelta(days=1)
            if dt.weekday() == cur_day.weekday() or tomorrow.weekday() == cur_day.weekday():
               fore = Fore.RED

            if self.ordered_daily_tasks(cur_day):
                print(fore + Style.BRIGHT + "Due " + cur_day.strftime('%a, %d %b') + Style.NORMAL)
                self.display_daily_tasks(cur_day)
            if day == 6:
                print(Style.RESET_ALL)

        if self.get_tasks_with_priority(Priority.HIGH):
            print(Fore.RED + Style.BRIGHT + "High Priority:" + Style.NORMAL)
            self.display_priority_tasks(Priority.HIGH)
            print(Style.RESET_ALL)

    def display_priority_tasks(self, priority):
        priority_tasks = self.get_tasks_with_priority(priority)

        for task in priority_tasks:
            print("   " + task.description)

    def display_all_tasks(self, today):
        tomorrow = today + timedelta(days = 1)
        # Filter for only tasks that are not completed and sort based on due_date
        todo_due = list(filter(lambda x: x.next_due_date(today), self.due_tasks))
        todo_due.sort(key = lambda x: x.next_due_date(today))

        if todo_due:
            print(Style.BRIGHT + Fore.RED + "\nDue Tasks:" + Style.RESET_ALL)

            for task in todo_due:
                fore = ""
                next_due_date = task.next_due_date(today)
                if next_due_date.date() == today.date() or next_due_date.date() == tomorrow.date():
                    fore = Fore.RED
                print(fore + DueTask.datetime_str(next_due_date, task.description) + Style.RESET_ALL)

        # Display all non-completed priority tasks in reverse order of priority
        high_priority = list(filter(lambda x: not x.completed,
                                    self.get_tasks_with_priority(Priority.HIGH)))
        if high_priority:
            print(Style.BRIGHT + Fore.RED + "\nHigh Priority:" + Style.NORMAL)
            for task in high_priority:
                print(Fore.RED + task.description + Style.RESET_ALL)

        medium_priority = list(filter(lambda x: not x.completed,
                                      self.get_tasks_with_priority(Priority.MEDIUM)))
        if medium_priority:
            print(Style.BRIGHT +  "\nMedium Priority:" + Style.NORMAL)
            for task in medium_priority:
                print(task.description)

        low_priority = list(filter(lambda x: not x.completed,
                                   self.get_tasks_with_priority(Priority.LOW)))
        if low_priority:
            print(Style.BRIGHT +  "\nLow Priority:" + Style.NORMAL)
            for task in low_priority:
                print(task.description)
        print("")

    # This displays everything due today and tomorrow, with completed tasks greyed out,
    # As well as high priority tasks
    def display_tasks(self, today):
        tomorrow = today + timedelta(days = 1)

        if self.ordered_daily_tasks(today):
            print(Fore.RED + Style.BRIGHT + "Due Today:" + Style.NORMAL)
            self.display_daily_tasks(today)
            print("")

        if self.ordered_daily_tasks(tomorrow):
            print(Fore.RED + Style.BRIGHT + "Due Tomorrow:" + Style.NORMAL)
            self.display_daily_tasks(tomorrow)
            print("")

        if self.get_tasks_with_priority(Priority.HIGH):
            print(Fore.RED + Style.BRIGHT + "High Priority:" + Style.NORMAL)
            self.display_priority_tasks(Priority.HIGH)
            print("")

    def display_today(self, now):
        print("")
        self.display_daily_schedule(now)
        print("")
        self.display_tasks(now)

    def display_week(self, now):
        print("")
        self.display_weekly_schedule(now)
        self.display_weekly_tasks(now)

    def find_due_task(self, task_str):
        matching_due = list(filter(lambda x:task_str.lower() in x.description.lower(),
                                   self.due_tasks))
        if matching_due:
            return matching_due[0]
        return None

    def find_priority_task(self, task_str):
        matching_priority = list(filter(lambda x:task_str.lower() in x.description.lower(),
                                        self.priority_tasks))
        if matching_priority:
            return matching_priority[0]
        return None

    def find_event(self, event_str):
        matching_events = list(filter(lambda x:event_str.lower() in x.description.lower(),
                                      self.events))
        if matching_events:
            return matching_events[0]
        return None

    def complete_task(self, task_str, today):
        due_task = self.find_due_task(task_str)
        if due_task:
            # Ask for confirmation before completing the task
            confirm = input(Style.BRIGHT + "\nComplete the following task? (y/n)\n" + Style.NORMAL + \
                            str(due_task) + "\n")
            if not confirm == "y":
                return
            due_task.completed.append(due_task.next_due_date(today))
            self.dump()
            return

        priority_task = self.find_priority_task(task_str)
        if priority_task:
            confirm = input(Style.BRIGHT + "\nComplete the following task? (y/n)\n" + Style.NORMAL + \
                            str(priority_task) + "\n")
            if not confirm == "y":
                return
            priority_task.completed = True
            self.dump()
            return

        raise InputError("Error: no matching task found.")

    def delete(self, delete_str):
        event = self.find_event(delete_str)
        if event:
            confirm = input(Style.BRIGHT + "\nDelete the following event? (y/n)\n" + Style.NORMAL + \
                            str(event) + "\n")
            if not confirm == "y":
                return
            self.events.remove(event)
            self.dump()
            return

        due_task = self.find_due_task(delete_str)
        if due_task:
            confirm = input(Style.BRIGHT + "\nDelete the following task? (y/n)\n" + Style.NORMAL + \
                            str(due_task) + "\n")
            if not confirm == "y":
                return
            self.due_tasks.remove(due_task)
            self.dump()
            return

        priority_task = find_priority_task(delete_str)
        if priority_task:
            confirm = input(Style.BRIGHT + "\nDelete the following task? (y/n)\n" + Style.NORMAL + \
                            str(priority_task) + "\n")
            if not confirm == "y":
                return
            self.priority_tasks.remove(priority_task)
            self.dump()
            return

        raise InputError("Error: no matching event or task found.")

    def load(self):
        with open(self.fname, 'r') as f:
            data = json.load(f, cls=serialize.CalendarDecoder)
        self.events = data['events']
        self.due_tasks = data['due_tasks']
        self.priority_tasks = data['priority_tasks']

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
    def add_due_task(self,
                     description,
                     due_dates,
                     days_delta=0,
                     exceptions=[],
                     enddate=None):
        self.due_tasks.append(DueTask(description,
                               due_dates,
                               Repeater(days_delta,
                                        exceptions,
                                        enddate) if days_delta else None,
                              completed = []))
        self.due_tasks.sort(key=lambda task: task.due_dates[0])
        self.dump()

    @drop_nones
    def add_priority_task(self,
                          description,
                          priority = Priority.LOW,
                          completed=False):
        bound_priority = max(Priority.LOW.value, min(priority, Priority.HIGH.value))
        self.priority_tasks.append(PriorityTask(description,
                                                Priority(bound_priority)))
        self.priority_tasks.sort(key=lambda task: task.priority.value, reverse=True)
        self.dump()
