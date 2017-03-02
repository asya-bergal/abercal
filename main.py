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

    try:
        # Make sure original dates are parsed successfully
        if args.datetimes:
            parsed_datetimes=list(map(lambda x: parse_datetime(x, timestamp), args.datetimes))
        # Make sure duration string is parsed successfully
        if args.duration:
            parsed_duration=parse_timedelta(args.duration)
        # If the event is repeating, make sure the exception dates and enddate
        # is parsed successfully
        if args.exceptions:
            parsed_exceptions=list(map(lambda x: parse_datetime(x, timestamp), args.datetimes))
        if args.enddate:
            parsed_enddate = parse_datetime(args.enddate, timestamp)

        # Add an event
        if args.event:
            calendar.add_event(args.event,
                            parsed_datetimes,
                            duration=parsed_duration,
                            location=args.location,
                            days_delta=int(args.days_delta) if args.days_delta else None,
                            exceptions=parsed_exceptions,
                            enddate=parsed_enddate)
        # Add a task
        elif args.task:
            calendar.add_task(args.task,
                            due_dates=parsed_datetimes,
                            priority=args.priority,
                            days_delta=int(args.days_delta) if args.days_delta else None,
                            exceptions=parsed_exceptions,
                            enddate=parsed_enddate)
    except InputError as err:
        print(err)

# TODO: If nothing, just show daily schedule + TODOS
if __name__ == "__main__":
    main()
