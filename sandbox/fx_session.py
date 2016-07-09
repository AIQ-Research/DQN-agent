__author__ = 'vicident'
__copyright__ = "Copyright 2016, AIQ-Research"
__credits__ = ["Denis Timoshenko"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Denis Timoshenko"
__email__ = "tnediciv@gmail.com"
__status__ = "Prototype"

from datetime import time, timedelta, datetime

class MarketSession:
    # datetime.time, session should be shorter than 24h
    def __init__(self, time_begin, time_end, period):
        self._time_begin = time_begin
        self._time_end = time_end
        self._period = period

    @staticmethod
    def datetime_to_ms(dt):
        return (dt - datetime.utcfromtimestamp(0)).total_seconds() * 1000

    @staticmethod
    def ms_to_datetime(ms):
        return datetime.utcfromtimestamp(ms/1000)

    def get_session_range(self, day):
        """
        :param day:
        :return:
        """
        session_start = datetime.combine(day, self._time_begin)
        session_end = datetime.combine(day, self._time_end)

        # next day, if reverse order
        if (session_end - session_start).total_seconds() < 0.0:
            session_end += timedelta(days=1)

        return self.datetime_to_ms(session_start), self.datetime_to_ms(session_end) - 1

    def get_session_period(self):
        #TODO: convert to deltatime
        return self._period


# 11:00 PM to 8:00 AM GMT
class AsianSession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(23, 0, 0), time(8, 0, 0), 24 * 3600 * 1000)


# 7:00 AM to 4:00 PM GMT
class EuropeanSession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(7, 0, 0), time(16, 0, 0), 24 * 3600 * 1000)


# noon to 8:00 PM GMT
class AmericanSession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(12, 0, 0), time(20, 0, 0), 24 * 3600 * 1000)


# European + American Session
# 7:00 AM to 8:00 PM GMT
class EASession(MarketSession):
    def __init__(self):
        MarketSession.__init__(self, time(7, 0, 0), time(20, 0, 0), 24 * 3600 * 1000)
