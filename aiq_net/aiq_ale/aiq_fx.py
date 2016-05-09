__author__ = 'vicident'
import pytz
from datetime import time, timedelta, datetime, tzinfo
from collections import namedtuple

# GMT - Greenwich Mean Time, UK
# UTC - Coordinated Universal Time
UTCTimeIntervals = namedtuple('UTCTimeIntervals', 'start_time end_time')
EPOCH = datetime.utcfromtimestamp(0)
LONDON_TZ = pytz.timezone('Europe/London')


def datetime_to_ms(dt):
    return (dt - EPOCH).total_seconds() * 1000.0


def utc_ms_to_str(utc_ms):
    dt = datetime.utcfromtimestamp(utc_ms/1000.0)
    london_dt = LONDON_TZ.localize(dt, is_dst=None)
    return london_dt.strftime('%a - %Y-%m-%d %H:%M:%S') + "," + str(utc_ms % 1000)


def is_summer_time(aware_dt):
    assert aware_dt.tzinfo is not None
    assert aware_dt.tzinfo.utcoffset(aware_dt) is not None
    return bool(aware_dt.dst())


def print_utc_time_intervals(intervals):
    for i in intervals:
        start_str = utc_ms_to_str(i.start_time)
        end_str = utc_ms_to_str(i.end_time)
        diff = timedelta(milliseconds=(i.end_time - i.start_time))
        print "[" + start_str + " <-> " + end_str + "]", diff


def add_day_ignore_daylight(dt, time):
    dt_next = dt + timedelta(days=1)
    return datetime.combine(dt_next, time)


class MarketSession:
    # datetime.time, session should be shorter than 24h
    def __init__(self, time_begin, time_end):
        self._time_begin = time_begin
        self._time_end = time_end

    # UTCTimeIntervals
    def extract_from_interval(self, time_interval_utc):
        sdt = datetime.utcfromtimestamp(time_interval_utc.start_time/1000)
        edt = datetime.utcfromtimestamp(time_interval_utc.end_time/1000)

        session_start = datetime.combine(sdt, self._time_begin)
        session_end = datetime.combine(sdt, self._time_end)

        # next day, if reverse order
        if (session_end - session_start).total_seconds() < 0.0:
            session_end += timedelta(days=1)

        intervals = []

        while (edt - session_end).total_seconds() >= 0.0:
            intervals.append(
                UTCTimeIntervals(
                    datetime_to_ms(session_start),
                    datetime_to_ms(session_end)
                )
            )
            session_start += timedelta(days=1)
            session_end += timedelta(days=1)

        return intervals


# 11:00 PM to 8:00 AM GMT
class AsianSession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(23, 0, 0), time(8, 0, 0))


# 7:00 AM to 4:00 PM GMT
class EuropeanSession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(7, 0, 0), time(16, 0, 0))


# noon to 8:00 PM GMT
class AmericanSession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(12, 0, 0), time(20, 0, 0))


# European + American Session
# 7:00 AM to 8:00 PM GMT
class EASession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(7, 0, 0), time(20, 0, 0))
