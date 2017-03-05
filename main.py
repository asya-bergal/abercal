import argparse

from util import *
from parse import *
from cal import Calendar

# - Add an event -e "description" -l "location" -d "starting_dates" -r "days-delta" -e "exceptions" -u "enddate"
# - Add an event -t "description" -l "priority" -d "due_dates" -r "days-delta" -e "exceptions" -u "enddate"
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c','--calendar', default='calendar')

    parser.add_argument('-s', '--show')
    parser.add_argument('-w', '--week', action='store_true')
    parser.add_argument('-td', '--today', action='store_true')

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
    timestamp = local_now()

    # TODO: Better error messages
    calendar = Calendar(args.calendar)

    parsed_datetimes = []
    parsed_exceptions = []
    parsed_duration = None
    parsed_enddate = None
    day_to_show = None

    try:
        # Make sure date to show schedule for is parsed correctly
        if args.show:
            day_to_show = parse_datetime(args.show, timestamp)
        # Make sure original dates are parsed successfully
        if args.datetimes:
            for x in args.datetimes:
                parsed_datetimes=list(map(lambda x: parse_datetime(x, timestamp), args.datetimes))
        # Make sure duration string is parsed successfully
        if args.duration:
            parsed_duration=parse_timedelta(args.duration)
        # If the event is repeating, make sure the exception dates and enddate
        # is parsed successfully
        if args.exceptions:
            parsed_exceptions=list(map(lambda x: parse_datetime(x, timestamp), args.exceptions))
        if args.enddate:
            parsed_enddate = parse_datetime(args.enddate, timestamp)

        # Display calendar
        if args.week:
            calendar.display_week(timestamp)
        elif args.today:
            calendar.display_today(timestamp)
        elif args.show:
            calendar.display_daily_schedule(day_to_show)
        # Add an event
        elif args.event:
            calendar.add_event(args.event,
                            parsed_datetimes,
                            duration=parsed_duration,
                            location=args.location,
                            days_delta=int(args.days_delta) if args.days_delta else None,
                            exceptions=parsed_exceptions,
                            enddate=parsed_enddate)
        # Add a task
        elif args.task:
            # Initialize a task to be low priority if no due-date is specified
            if not args.datetimes and not args.priority:
                args.priority = 1
            calendar.add_task(args.task,
                            due_dates=parsed_datetimes,
                            priority=int(args.priority) if args.priority else None,
                            days_delta=int(args.days_delta) if args.days_delta else None,
                            exceptions=parsed_exceptions,
                            enddate=parsed_enddate)
        else:
            calendar.display_today(timestamp)

    except InputError as err:
        print(err)

# TODO: If nothing, just show daily schedule + TODOS
if __name__ == "__main__":
    main()
