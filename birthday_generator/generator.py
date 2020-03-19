from datetime import datetime

import pytz
from icalendar import Calendar, Event
from zhdate import ZhDate


class Birthday:
    def __init__(self, name: str, year: int, month: int, day: int, is_lunar):
        self.day = day
        self.month = month
        self.year = year
        self.name = name
        self.is_lunar = is_lunar

    def __str__(self):
        return f"{self.name}, birthday=({self.year},{self.month},{self.day}), is_lunar={self.is_lunar}"

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
            name, birthday, is_lunar = line.strip("\n").split(",")
            birthday_array = [int(item) for item in birthday.split("/")]
            birthday = Birthday(name, *birthday_array, is_lunar[0] == "Y")
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
    tz = pytz.timezone('Asia/Shanghai')
    for birthday, date in event_list:
        print(birthday, date)
        event = Event()
        age = date[0] - birthday.year
        event.add("summary", f"{birthday.name}'s {age} years old birthday")
        event.add('dtstart', datetime(*date, 0, 0, 0, tzinfo=tz))
        event.add('dtend', datetime(*date, 23, 59, 59, tzinfo=tz))
        event.add('dtstamp', datetime.now())
        cal.add_component(event)
    with open("birthday.ics", "wb") as f:
        f.write(cal.to_ical())

if __name__=="__main__":
    contacts = read_csv('../birthday.csv')
    events = generate_birthdays(contacts, 10)
    generate_ics(events)
