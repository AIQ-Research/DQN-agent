__author__ = 'vicident'

from aiq_net.interfaces.ile import ILearningEnvironment
from aiq_net.aiq_db.connectors import SqliteConnector
from collections import namedtuple
import numpy as np
import datetime

UTCTimeIntervals = namedtuple('UTCTimeIntervals', 'start_time end_time')

def utc_ms_to_str(utc_ms):
    return datetime.datetime.fromtimestamp(utc_ms/1000.0).strftime('%a - %Y-%m-%d %H:%M:%S') + "," + str(utc_ms % 1000)

def print_utc_time_intervals(intervals):
    for i in intervals:
        start_str = utc_ms_to_str(i.start_time)
        end_str = utc_ms_to_str(i.end_time)
        print "[" + start_str + " <-----> " + end_str + "]"

# Two active threads meet here: trainer thread and market listener thread
class FxLocalALE(ILearningEnvironment):

    def __init__(self, db_path):
        self._connect_fx_db_(db_path)
        self._check_time_periods_()
        self._update_time_periods_()

    def _connect_fx_db_(self, db_path):
        self.db = SqliteConnector()
        self.db.connect(db_path)

    def _check_time_periods_(self):
        table_names = self.db.get_tables()
        base_time_column = []
        base_table_name = ''

        if not len(table_names):
            raise Exception("Empty Database")

        for table_name in table_names:
            columns = self.db.get_table_columns(table_name)

            if 'time' not in columns:
                raise Exception("table \'" + table_name + "\' from database \'" + self.db.get_name() +
                                "\' doesn't have required \'time\' column")

            if not len(base_time_column):
                base_time_column = self.db.read_table_column(table_name, 'time', 1)
                base_table_name = table_name
            else:
                time_column = self.db.read_table_column(table_name, 'time', 1)

                if not time_column == base_time_column:
                    raise Exception("tables \'" + base_table_name + "\' and \'" + table_name + "\' are not synchronized")

    def _update_time_periods_(self):
        table_names = self.db.get_tables()

        # read time from the first table (table index doesn't matter, if _check_time_periods_ has been passed)
        time_column = self.db.read_table_column(table_names[0], 'time', 1)

        np_time_vector = np.array(time_column)
        time_diff = np.diff(np_time_vector)

        # find base (minimal) period of data changing (MS, SEC, MIN...)
        self._period = np.min(time_diff)

        # find all periods larger than base period
        time_diff -= self._period
        break_points = np.nonzero(time_diff)
        self._time_intervals = []
        start_time = np_time_vector[0]

        for bp in break_points[0].tolist():
            end_time = np_time_vector[bp]
            self._time_intervals.append(UTCTimeIntervals(start_time, end_time))
            start_time = np_time_vector[bp + 1]

        end_time = np_time_vector[-1]
        self._time_intervals.append(UTCTimeIntervals(start_time, end_time))

        print_utc_time_intervals(self._time_intervals)
        print "[OK] Time intervals (" + str(len(self._time_intervals)) + ")"


    def load_tge_from_json(self, json):
        pass

    def act(self, action):
        pass

    def game_over(self):
        pass

    def reset_game(self):
        pass

    def getMinimalActionSet(self): pass

    def getScreenDims(self): pass

    def lives(self): pass

    # write aiq data here
    def getScreenGrayscale(self, screen_buffer):
        pass
