# abercal

A command line calendar with the features I want, narcistically named after me.
Still in progress and not recommended for public use.

Somewhat unique features?
- Datestring parsing
- Repeated tasks
- JSON storage designed to be human read/edit-able

## Usage

### Create a New Calendar

```bash
# Create a new custom calendar with the name "funcal", stored in "funcal.json" 
python main.py -c funcal
```

### Add an Event

```bash
# Add a new event to the default calendar at 7pm tomorrow.
python main.py -e "Burning with Brandon" -dt "tomorrow 7pm"

# Add a new event to the calendar "funcal" with a custom length and location
python main.py -c funcal -e "Watching Anime" -dt "today 5pm" -len "1.5 hours" -loc "Projector Room"

# Add a repeating event to the default calendar which starts next Tuesday and Thursday,
# repeats every 7 days, and goes until June 9, with June 2nd as an exception.
python main.py -e "Arson Lecture" -dt "tuesday 2pm" "thursday 2pm" -r 7 -u "june 9" -ex "june 2"
```

### Add a Task

#### With Due Dates
```bash
# Add a new task with a single due date
python main.py -t "Rent Bitcoin" -due "two weeks from now"

# Add a repeating task
python main.py -t "Thermo Pset" -due "friday 5pm" -r 7 -u "june 9"
```

#### With a Priority

```bash
# Add a task with a priority in the range [1-3]
python main.py -t "Stop and smell the roses" -p 3
```

### Complete a Task
```bash
# Complete the nearest instance of a task specified by a substring.
# You will be asked for confirmation.
python main.py -f "thermo pset"
```

### Delete
```bash
# Delete an entire event or task specified by a substring.
# You will be asked for confirmation.
python main.py -del "Burning"
```

### Show Calendar

#### Default View
```bash
# Show today's schedule, tasks due in the next two days, and high priority tasks.
python main.py
```
#### Weekly View
```bash
# Show this week's schedule, tasks due this week, and high priority tasks.
python main.py -week
```
#### Day View
```bash
# Show the schedule on a particular day
python main.py -day "saturday"
```
#### Show all Tasks
```bash
# Show all non-completed future tasks in decreasing order of due date and priority.
python main.py -tasks
```

