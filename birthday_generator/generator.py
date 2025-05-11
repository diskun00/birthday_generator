from datetime import datetime, timedelta

import pytz
from icalendar import Calendar, Event, Alarm
from zhdate import ZhDate


class Birthday:
    def __init__(self, name: str, year: int, month: int, day: int, is_lunar, vip=0):
        self.day = day
        self.month = month
        self.year = year
        self.name = name
        self.is_lunar = is_lunar
        self.vip = vip

    def __str__(self):
        return f"{self.name}, birthday=({self.year},{self.month},{self.day}), is_lunar={self.is_lunar}, vip={self.vip}"

    def __repr__(self):
        return str(self)

    def in_year(self, year):
        """
        return birth day in $year
        :param year:
        :return:
        """
        argument = year, self.month, self.day
        return self.lunar_to_solar(*argument) if self.is_lunar else argument

    @classmethod
    def lunar_to_solar(cls, year: int, month: int, day: int):
        """
        convert lunar date to solar date
        :param year:
        :param month:
        :param day:
        :return: solar date
        """
        lunar = ZhDate(year, month, day)
        solar_datetime = lunar.to_datetime()
        return solar_datetime.year, solar_datetime.month, solar_datetime.day


def read_csv(csv_file):
    """
    read birthday csv data and converted to solar date format in list
    :param csv_file:
    :return: solar date format in list
    """
    birthday_list = []
    with open(csv_file, 'r') as f:
        for line in f.readlines()[1:]:
            parts = line.strip("\n").split(",")
            name, birthday, is_lunar = parts[:3]
            vip = parts[3] if len(parts) > 3 else 0
            birthday_array = [int(item) for item in birthday.split("/")]
            birthday = Birthday(name, *birthday_array, is_lunar[0] == "Y", int(vip) if vip else 0)
            birthday_list.append(birthday)
    return birthday_list


def generate_birthdays(birthdays: list, year_to_generate: int):
    """
    generate birthdays from lists
    :param birthdays:
    :param year_to_generate: how many year from this year to add to the event
    :return:
    """
    this_year = datetime.now().year
    event_list = []
    for birthday in birthdays:
        for year in range(this_year, this_year + year_to_generate):
            # Skip events that have already passed this year
            today = datetime.now()
            event_date = datetime(*birthday.in_year(year))
            if year == this_year and event_date < today:
                continue
            date = birthday.in_year(year)
            event_list.append([birthday, date])
    return event_list


def generate_ics(event_list: list):
    """
    generate ics file
    :param event_list: [birthday, [year, month, day]]
    :return:
    """
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    tz = pytz.timezone('Europe/Berlin')
    # tz = pytz.timezone('Asia/Shanghai')
    for birthday, date in event_list:
        print(birthday, date)
        event = Event()
        age = date[0] - birthday.year
        if birthday.year < 0:
            event.add("summary", f"🎂 {birthday.name} birthday🎂")
        else:
            event.add("summary", f"🎂 {birthday.name} {age} years old birthday🎂")

        if birthday.vip:
            # Add notifications/alarms for VIP contacts
            # 14 days before
            alarm14 = Alarm()
            alarm14.add('action', 'DISPLAY')
            alarm14.add('description', f"Upcoming birthday for {birthday.name} in 2 weeks")
            alarm14.add('trigger', timedelta(days=-14))
            event.add_component(alarm14)

            # 10 days before
            alarm10 = Alarm()
            alarm10.add('action', 'DISPLAY')
            alarm10.add('description', f"Upcoming birthday for {birthday.name} in 10 days")
            alarm10.add('trigger', timedelta(days=-10))
            event.add_component(alarm10)

            # 1 week before 
            alarm7 = Alarm()
            alarm7.add('action', 'DISPLAY')
            alarm7.add('description', f"Upcoming birthday for {birthday.name} in 1 week")
            alarm7.add('trigger', timedelta(days=-7))
            event.add_component(alarm7)

            # 1 day before
            alarm1 = Alarm()
            alarm1.add('action', 'DISPLAY')
            alarm1.add('description', f"Upcoming birthday for {birthday.name} tomorrow")
            alarm1.add('trigger', timedelta(days=-1))
            event.add_component(alarm1)

        # 3 days before
        alarm3 = Alarm()
        alarm3.add('action', 'DISPLAY')
        alarm3.add('description', f"Upcoming birthday for {birthday.name} in 3 days")
        alarm3.add('trigger', timedelta(days=-3))
        event.add_component(alarm3)

        # On the day
        alarm0 = Alarm()
        alarm0.add('action', 'DISPLAY')
        alarm0.add('description', f"Today is {birthday.name}'s birthday!")
        alarm0.add('trigger', timedelta(days=0))
        event.add_component(alarm0)

        event.add('dtstart', datetime(*date, 7, 0, 0))
        event.add('dtend', datetime(*date, 21, 00, 00))
        event.add('dtstamp', datetime.now())
        event.add('description', f"They were born on {birthday.year}/{birthday.month}/{birthday.day} ({'Lunar' if birthday.is_lunar else 'Solar'} calendar)")
        cal.add_component(event)
    
    # Add end of year reminder to generate next year's calendar
    reminder = Event()
    reminder.add('summary', "!!Generate next year's birthday calendar")
    reminder.add('dtstart', datetime(date[0], 12, 31, 7, 0, 0))
    reminder.add('dtend', datetime(date[0], 12, 31, 21, 0, 0))
    reminder.add('dtstamp', datetime.now())
    reminder.add('description', "Time to generate the birthday calendar for next year!")
    
    # Add alarms for the reminder
    alarm7 = Alarm()
    alarm7.add('action', 'DISPLAY') 
    alarm7.add('description', "Generate next year's birthday calendar in 1 week")
    alarm7.add('trigger', timedelta(days=-7))
    reminder.add_component(alarm7)

    alarm0 = Alarm()
    alarm0.add('action', 'DISPLAY')
    alarm0.add('description', "Generate next year's birthday calendar today!")
    alarm0.add('trigger', timedelta(days=0))
    reminder.add_component(alarm0)

    cal.add_component(reminder)
    with open("birthday.ics", "wb") as f:
        f.write(cal.to_ical())

if __name__=="__main__":
    contacts = read_csv('../birthday.csv')
    events = generate_birthdays(contacts, 1)
    generate_ics(events)
