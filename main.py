import argparse

from util import *
from parse import *
from cal import Calendar

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--calendar', default='calendar')

    # ADD EVENT:
    # Mandatory: -e description, -dt start_times, -len duration
    # Optional: -len duration (defaults to 1 hour)
    #           -loc location, -r days_delta, -ex exceptions, -u enddate to specify a repeater.
    parser.add_argument('-e','--event')
    parser.add_argument('-dt','--dates', nargs='+')
    parser.add_argument('-len','--duration')
    parser.add_argument('-loc','--location')

    parser.add_argument('-r','--days-delta')
    parser.add_argument('-ex','--exceptions', nargs='+')
    parser.add_argument('-u','--enddate')

    # ADD DUE TASK
    # Mandatory: -t description, -due due_dates
    # Optional: -r days_delta, -ex exceptions, -u enddate to specify a repeater.
    parser.add_argument('-t','--task')
    parser.add_argument('-due','--due-dates', nargs='+')

    # ADD PRIORITY TASK -t <description
    # Mandatory: -t description
    # Optional: -p priority (defaults to Priority.LOW)
    parser.add_argument('-p','--priority')

    # COMPLETE TASK
    # Mandatory: -f task description substring to search
    parser.add_argument('-f','--finish')

    # EDIT
    # Mandatory: -edit description substring to search
    # Optional: any number of arguments to edit
    parser.add_argument('-edit','--edit')

    # DELETE
    # Mandatory: -del description substring to search
    parser.add_argument('-del','--delete')

    # SHOW
    # Mandatory: -s description substring to search
    parser.add_argument('-s','--show')

    # DISPLAY
    # -day Display schedule for day to display
    # -today Display today's schedule + todos
    # -week Display weekly schedule + todos
    # -todo Display all todos
    parser.add_argument('-day', '--day')
    parser.add_argument('-week', '--week', action='store_true')
    parser.add_argument('-today', '--today', action='store_true')
    parser.add_argument('-todo', '--todo', action='store_true')

    args = parser.parse_args()

    # Record timestamp to produce consistent output with respect to dateparser
    timestamp = local_now()

    # TODO: Better error messages
    calendar = Calendar(args.calendar)

    parsed_dates = []
    parsed_due_dates = []
    parsed_exceptions = []
    parsed_duration = None
    parsed_enddate = None
    parsed_day = None

    try:
        # Make sure original dates are parsed successfully
        if args.dates:
            parsed_dates=list(map(lambda x: parse_datetime(x, timestamp), args.dates))
        if args.due_dates:
            parsed_due_dates=list(map(lambda x: parse_datetime(x, timestamp), args.due_dates))
        # Make sure length string is parsed successfully
        if args.duration:
            parsed_duration=parse_timedelta(args.duration)
        # If the event is repeating, make sure the exception dates and enddate
        # is parsed successfully
        if args.exceptions:
            parsed_exceptions=list(map(lambda x: parse_datetime(x, timestamp), args.exceptions))
        if args.enddate:
            parsed_enddate = parse_datetime(args.enddate, timestamp)
        # Make sure date to show schedule for is parsed correctly
        if args.day:
            parsed_day = parse_datetime(args.day, timestamp)

        # Display calendar
        if args.week:
            calendar.display_week(timestamp)
        elif args.today:
            calendar.display_today(timestamp)
        elif args.day:
            calendar.display_daily_schedule(parsed_day)
        elif args.todo:
            calendar.display_all_tasks(timestamp)
        # Complete a task
        elif args.finish:
            calendar.complete_task(args.finish, timestamp)
        # Delete something
        elif args.delete:
            calendar.delete(args.delete)
        # Add an event
        elif args.event:
            calendar.add_event(args.event,
                               parsed_dates,
                               duration=parsed_duration,
                               location=args.location,
                               days_delta=int(args.days_delta) if args.days_delta else None,
                               exceptions=parsed_exceptions,
                               enddate=parsed_enddate)
        # Add a task
        elif args.task:
            if args.due_dates:
                calendar.add_due_task(args.task,
                                      parsed_due_dates,
                                      days_delta=int(args.days_delta) if args.days_delta else None,
                                      exceptions=parsed_exceptions,
                                      enddate=parsed_enddate)
            else:
                # Initialize a task to be low priority if no due-date or priority is specified
                if not args.priority:
                    args.priority = 1
                calendar.add_priority_task(args.task,
                                           int(args.priority))
        else:
            calendar.display_today(timestamp)

    except InputError as err:
        print(err)

# TODO: If nothing, just show daily schedule + TODOS
if __name__ == "__main__":
    main()
