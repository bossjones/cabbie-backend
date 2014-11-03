import datetime


def week_of_month(date):
    return (date.day - 1) // 7 + 1
