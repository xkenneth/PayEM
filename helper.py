from mx.DateTime import Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
from mx.DateTime import now
from mx.DateTime import RelativeDateTime


### Time Helpers ###
def previous_sunday(dt):
    """Return the previous Sunday from the current date."""
    return dt - RelativeDateTime(days=(dt.day_of_week+1))

def two_weeks_ago(dt):
    """Return 14 days from the previous date."""
    return dt - RelativeDateTime(days=13)

def days_ago(dt,n):
    """Return N-1 days from the previous date."""
    return dt - RelativeDateTime(days=n-1)

def start_day(dt):
    """Returns a ts to the start of the day."""
    return dt - RelativeDateTime(hours=dt.hour,minutes=dt.minute,seconds=dt.second)

def end_day(dt):
    return dt + RelativeDateTime(hours=23-dt.hour,minutes=59-dt.minute,seconds=59-dt.second)

### BaseCamp Helpers ###x

    
if __name__ == '__main__':
    print previous_sunday(now())
    print two_weeks_ago(previous_sunday(now()))
    print start_day(now())
    print end_day(now())
