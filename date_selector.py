from datetime import timedelta, datetime
from pprint import pprint
from copy import copy

from dateutil import parser


def get_bookable_week(a):
    """
        This will parse a list of days and create a single consecutive week.

        If you give it a list of dates that are not consecutive it will find atleast two bookable days.
    """
    unbookable_week = []
    available = copy(a)
    # Gets the range of available dates and sorts them.
    available.sort()
    # Parses the range of date string into datetime objects.
    available_parsed = [parser.parse(x) for x in available]
    # Sorts the datetime objects
    available_parsed.sort()

    for date in available_parsed:
        if date > (datetime.now() + timedelta(weeks=47)):
            unbookable_week.append(date)

    if is_consecutive(available_parsed):
        print('Week is consecutive and bookable')
        return available_parsed
    else:
        print('Week isn\'t consecutive and needs to be reduced')
        bookable_week = []

        # This code is ugly, but I wrote it quickly.
        #
        # Basically I am looking for holes in a range, but I am just adding everything and taking out duplicate later.
        # Barf.
        for date in available_parsed:
            next_day = date + timedelta(days=1)
            if next_day in available_parsed:
                bookable_week.append(date)
                bookable_week.append(next_day)

        last_day = bookable_week[-1]
        if last_day + timedelta(days=1) in available_parsed:
            bookable_week.append(last_day + timedelta(days=1))

        bookable_week = list(set(bookable_week))
        bookable_week.sort()
        return bookable_week


def is_consecutive(date_list):
    date_ints = set([d.toordinal() for d in date_list])

    if max(date_ints) - min(date_ints) == len(date_ints) - 1:
        return True
    else:
        return False


def get_bookable_days(a):
    dates = get_bookable_week(a)
    print(dates)
    check_in_dates = {
        'in': min(dates).strftime("%Y-%m-%d"),
        'out': max(dates).strftime("%Y-%m-%d")
    }
    return check_in_dates
