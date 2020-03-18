from datetime import datetime

import pytz
from LunarSolarConverter.LunarSolarConverter import Solar, LunarSolarConverter
from icalendar import Calendar, Event


class Birthday:
    def __init__(self, name: str, year: int, month: int, day: int):
        self.day = day
        self.month = month
        self.year = year
        self.name = name

    def __str__(self):
        return f"{self.name}, birthday=({self.year},{self.month},{self.day})"

    def __repr__(self):
        return str(self)


def lunar_to_solar(year: int, month: int, day: int):
    """
    convert lunar date to solar date
    :param year:
    :param month:
    :param day:
    :return: solar date
    """
    converter = LunarSolarConverter()
    solar = Solar(year, month, day)
    lunar = converter.SolarToLunar(solar)
    return lunar.lunarYear, lunar.lunarMonth, lunar.lunarDay


def read_csv(csv_file, years_to_add):
    """
    read birthday csv data and converted to solar date format in list
    :param csv_file:
    :param years_to_add: how many year from this year to add to the event
    :return: solar date format in list
    """
    birthday_list = []
    with open(csv_file, 'r') as f:
        for line in f.readlines()[1:]:
            name, birthday, is_lunar = line[:-1].split(",")
            birthday_array = [int(item) for item in birthday.split("/")]
            birthday = Birthday(name, *birthday_array)
            this_year = datetime.now().year
            for year in range(this_year, this_year + years_to_add):
                if is_lunar[0]:
                    date = lunar_to_solar(year, birthday_array[1], birthday_array[2])
                else:
                    date = year, birthday_array[1], birthday_array[2]
                birthday_list.append([birthday, date])
    return birthday_list


def generate_ics(birthday_list: list):
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    tz = pytz.timezone('Asia/Shanghai')
    for birthday, date in birthday_list:
        event = Event()
        age = date[0] - birthday.year
        event.add("summary", f"{birthday.name}'s {age} years old birthday")
        event.add('dtstart', datetime(*date, 0, 0, 0, tzinfo=tz))
        event.add('dtend', datetime(*date, 23, 59, 59, tzinfo=tz))
        event.add('dtstamp', datetime.now())
        cal.add_component(event)
        break
    with open("sample.ics", "wb") as f:
        f.write(cal.to_ical())


csv = read_csv('../birthday.csv', 10)
generate_ics(csv)
