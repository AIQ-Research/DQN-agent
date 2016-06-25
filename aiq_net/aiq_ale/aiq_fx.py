__author__ = 'vicident'
import pytz
from datetime import time, timedelta, datetime, tzinfo
from collections import namedtuple
import numpy as np

# GMT - Greenwich Mean Time, UK
# UTC - Coordinated Universal Time
UTCTimeIntervals = namedtuple('UTCTimeIntervals', 'start_time end_time')
IntervalSessions = namedtuple('IntervalSessions', 'interval sessions')
EPOCH = datetime.utcfromtimestamp(0)
LONDON_TZ = pytz.timezone('Europe/London')


def interval_len(interval):
    return interval.end_time - interval.start_time


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


def print_utc_time_interval(interval_ms):
    start_str = utc_ms_to_str(interval_ms.start_time)
    end_str = utc_ms_to_str(interval_ms.end_time)
    diff = timedelta(milliseconds=(interval_ms.end_time - interval_ms.start_time))
    print "[" + start_str + " <-> " + end_str + "]", diff


def print_utc_time_intervals(intervals_ms):
    for i in intervals_ms:
        print_utc_time_interval(i)


def add_day_ignore_daylight(dt, time):
    dt_next = dt + timedelta(days=1)
    return datetime.combine(dt_next, time)


class MarketSession:
    # datetime.time, session should be shorter than 24h
    def __init__(self, time_begin, time_end):
        self._time_begin = time_begin
        self._time_end = time_end

    # UTCTimeIntervals, sorted
    def extract_from_interval(self, time_interval_utc):
        sdt = datetime.utcfromtimestamp(time_interval_utc.start_time/1000)
        edt = datetime.utcfromtimestamp(time_interval_utc.end_time/1000)

        session_start = datetime.combine(sdt, self._time_begin)
        session_end = datetime.combine(sdt, self._time_end)

        # next day, if reverse order
        if (session_end - session_start).total_seconds() < 0.0:
            session_end += timedelta(days=1)

        sessions = []

        while (edt - session_end).total_seconds() >= 0.0:
            sessions.append(
                UTCTimeIntervals(
                    datetime_to_ms(session_start),
                    datetime_to_ms(session_end) - 1
                )
            )
            session_start += timedelta(days=1)
            session_end += timedelta(days=1)

        return sessions

    def extract_from_time_ids(self, time_vector, beg_id, end_id, period_ms):
        time_interval = UTCTimeIntervals(time_vector[beg_id], time_vector[end_id])
        sessions_ms = self.extract_from_interval(time_interval)
        sessions_id = []
        for sess_ms in sessions_ms:
            sess_begin_id = int((sess_ms.start_time - time_interval.start_time) / period_ms) + beg_id
            sess_end_id = int((sess_ms.end_time - time_interval.start_time) / period_ms) + beg_id
            sessions_id.append([sess_begin_id, sess_end_id])
        return sessions_id

    # check time point in exact session
    def check(self, time_utc_ms):
        dt = datetime.utcfromtimestamp(time_utc_ms/1000)
        t = time(dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
        if self._time_end > self._time_begin:
            flag_in = (t >= self._time_begin and t < self._time_end)
        else:
            flag_in = (t >= self._time_begin or t < self._time_end)
        return flag_in


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


# Session statistics
class SessionPreprocessing:
    def __init__(self, fx_buffer):
        h, w = fx_buffer.shape
        self._min = np.zeros((h, 1), dtype=np.float32)
        self._max = np.zeros((h, 1), dtype=np.float32)
        for i in range(h):
            self._min[i] = np.min(fx_buffer[i, :])*0.8
            self._max[i] = np.max(fx_buffer[i, :])*1.2

    def process(self, fx_buffer):
        preprocessed = (fx_buffer - self._min) / (self._max - self._min)
        fx_out = np.clip(preprocessed, 0, 1)
        return fx_out