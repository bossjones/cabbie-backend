import datetime
import calendar

def week_of_month(date):
    c = calendar.Calendar() 
    for i, weekdates in enumerate(c.monthdatescalendar(date.year, date.month)):
        if date in weekdates:
            return i + 1 
    return 0    # should not be reached
