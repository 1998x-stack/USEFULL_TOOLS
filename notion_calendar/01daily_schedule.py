from icalendar import Calendar, Event, Todo, Alarm
from datetime import datetime, timedelta
import pytz

def create_ics_file():
    # Create a calendar
    cal = Calendar()
    cal.add('prodid', '-//My Calendar//mxm.dk//')
    cal.add('version', '2.0')

    # Timezone setup
    timezone = pytz.timezone('Asia/Shanghai')  # Set your desired timezone

    # 1. 每天早上7点五分进行冥想，持续15分钟
    event_meditation = Event()
    event_meditation.add('summary', '冥想')
    event_meditation.add('dtstart', datetime(2025, 2, 20, 7, 5, tzinfo=timezone))
    event_meditation.add('duration', timedelta(minutes=15))
    event_meditation.add('rrule', {'freq': 'daily'})  # Repeat daily
    event_meditation.add('description', '每天早上7:05进行15分钟的冥想')

    # Add alarm for meditation
    alarm_meditation = Alarm()
    alarm_meditation.add('trigger', timedelta(minutes=-5))  # Reminder 5 minutes before
    alarm_meditation.add('action', 'DISPLAY')
    alarm_meditation.add('description', '马上开始冥想！')
    event_meditation.add_component(alarm_meditation)

    cal.add_component(event_meditation)

    # 2. 早上7点烧水，持续2分钟，7点20 刷牙洗脸，持续十分钟，7点30喝热水，持续十分钟
    # Burn water from 7:00 -7:02
    event_burn_water = Event()
    event_burn_water.add('summary', '烧水')
    event_burn_water.add('dtstart', datetime(2025, 2, 20, 7, 0, tzinfo=timezone))
    event_burn_water.add('duration', timedelta(minutes=2))
    event_burn_water.add('rrule', {'freq': 'daily'})  
    event_burn_water.add('description', '早上7点烧水，准备运动')

    alarm_burn_water = Alarm()
    alarm_burn_water.add('trigger', timedelta(minutes=-1))
    alarm_burn_water.add('action', 'DISPLAY')
    alarm_burn_water.add('description', '记得烧水！')
    event_burn_water.add_component(alarm_burn_water)

    cal.add_component(event_burn_water)

    # Brush teeth and wash face from 7:20-7:30
    event_brush_teeth = Event()
    event_brush_teeth.add('summary', '刷牙洗脸')
    event_brush_teeth.add('dtstart', datetime(2025, 2, 20, 7, 20, tzinfo=timezone))
    event_brush_teeth.add('duration', timedelta(minutes=10))
    event_brush_teeth.add('rrule', {'freq': 'daily'})  
    event_brush_teeth.add('description', '早上7:20刷牙洗脸')

    alarm_brush_teeth = Alarm()
    alarm_brush_teeth.add('trigger', timedelta(minutes=-1))
    alarm_brush_teeth.add('action', 'DISPLAY')
    alarm_brush_teeth.add('description', '开始刷牙洗脸！')
    event_brush_teeth.add_component(alarm_brush_teeth)

    cal.add_component(event_brush_teeth)

    # Drink hot water from 7:30-7:40
    event_drink_water = Event()
    event_drink_water.add('summary', '喝热水')
    event_drink_water.add('dtstart', datetime(2025, 2, 20, 7, 30, tzinfo=timezone))
    event_drink_water.add('duration', timedelta(minutes=10))
    event_drink_water.add('rrule', {'freq': 'daily'})  
    event_drink_water.add('description', '早上7:30喝热水，补充水分')

    alarm_drink_water = Alarm()
    alarm_drink_water.add('trigger', timedelta(minutes=-1))
    alarm_drink_water.add('action', 'DISPLAY')
    alarm_drink_water.add('description', '记得喝热水！')
    event_drink_water.add_component(alarm_drink_water)

    cal.add_component(event_drink_water)

    # 3. 早上9点上班，持续30分钟
    event_work = Event()
    event_work.add('summary', '上班')
    event_work.add('dtstart', datetime(2025, 2, 20, 9, 0, tzinfo=timezone))
    event_work.add('duration', timedelta(minutes=30))
    event_work.add('rrule', {'freq': 'daily'})  
    event_work.add('description', '早上9点上班')

    alarm_work = Alarm()
    alarm_work.add('trigger', timedelta(minutes=0))  # Reminder at event start
    alarm_work.add('action', 'DISPLAY')
    alarm_work.add('description', '上班时间到了！')
    event_work.add_component(alarm_work)

    cal.add_component(event_work)

    # 4. 每周一到每周五 七点20到八点半，去复旦游泳馆游泳
    event_swim = Event()
    event_swim.add('summary', '复旦游泳馆游泳')
    event_swim.add('dtstart', datetime(2025, 2, 20, 7, 20, tzinfo=timezone))
    event_swim.add('duration', timedelta(hours=1, minutes=10))  # 7:20-8:30 is 1h10m
    event_swim.add('rrule', {
        'freq': 'weekly',
        'wkst': 'MO',
        'until': datetime(2026, 2, 20, tzinfo=timezone),
        'byday': ['MO', 'TU', 'WE', 'TH', 'FR']
    })  
    event_swim.add('description', '每周一到周五早上7:20-8:30去复旦游泳馆游泳')

    # Add alarm for swimming
    alarm_swim = Alarm()
    alarm_swim.add('trigger', timedelta(minutes=-15))  # Reminder 15 minutes before
    alarm_swim.add('action', 'DISPLAY')
    alarm_swim.add('description', '马上去游泳！')
    event_swim.add_component(alarm_swim)

    cal.add_component(event_swim)

    # TODO tasks
    # 每天早晨6点洗漱喝水
    todo_morning_routine = Todo()
    todo_morning_routine.add('uid', 'morning-routine')
    todo_morning_routine.add('summary', '早晨6点洗漱喝水')
    todo_morning_routine.add('due', datetime(2025, 2, 20, 6, 0, tzinfo=timezone))
    todo_morning_routine.add('rrule', {'freq': 'daily'})

    # Add alarm for todo
    alarm_todo = Alarm()
    alarm_todo.add('trigger', timedelta(minutes=-10))  # Reminder 10 minutes before due
    alarm_todo.add('action', 'DISPLAY')
    alarm_todo.add('description', '赶紧洗漱喝水！')
    todo_morning_routine.add_component(alarm_todo)

    cal.add_component(todo_morning_routine)

    # 每周一早上的早餐需求
    todo_monday_breakfast = Todo()
    todo_monday_breakfast.add('uid', 'monday-breakfast')
    todo_monday_breakfast.add('summary', '周一早上的早餐需求')
    todo_monday_breakfast.add('due', datetime(2025, 2, 25, 6, 30, tzinfo=timezone))  # Example Monday
    todo_monday_breakfast.add('rrule', {
        'freq': 'weekly',
        'wkst': 'MO',
        'byday': 'MO'
    })

    # Add alarm for todo
    alarm_monday_breakfast = Alarm()
    alarm_monday_breakfast.add('trigger', timedelta(minutes=-20))  # Reminder 20 minutes before due
    alarm_monday_breakfast.add('action', 'DISPLAY')
    alarm_monday_breakfast.add('description', '准备周一早餐！')
    todo_monday_breakfast.add_component(alarm_monday_breakfast)

    cal.add_component(todo_monday_breakfast)

    # Save the calendar to a file
    with open('daily_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())

if __name__ == "__main__":
    create_ics_file()
    print("ICS file created successfully!")