#/bin/sh

rm testcal.json
python main.py -c "testcal" -e "event1" -dt "today 1pm" -d "1 hour"
python main.py -c "testcal" -e "event2" -dt "today 5pm" -l "some location"
python main.py -c "testcal" -e "event3" -dt "now"
python main.py -c "testcal" -e "event4" -dt "today 11pm"
python main.py -c "testcal" -e "event5" -dt "tomorrow 7pm"
python main.py -c "testcal" -e "repeating event 1" -dt "today 4pm" -r 2
python main.py -c "testcal" -e "repeating event 2" -dt "today 6pm" -r 1 -ex tomorrow -u friday

python main.py -c "testcal" -t "task1" -dt "today 6pm"
python main.py -c "testcal" -t "task2" -dt "today 7pm"
python main.py -c "testcal" -t "repeating task 1" -dt "today 8pm" -r 7
python main.py -c "testcal" -t "repeating task 2" -dt "today 9pm" -r 1 -ex tuesday -u friday
python main.py -c "testcal" -t "task3" -p 3
python main.py -c "testcal" -t "task4" -p 1

python main.py -c "testcal" 
