__author__ = 'vicident'

from aiq_net.interfaces.ile import ILearningEnvironment
from aiq_net.aiq_db.connectors import SqliteConnector
import numpy as np

from aiq_fx import UTCTimeIntervals, print_utc_time_interval, EASession, utc_ms_to_str


# Two active threads meet here: trainer thread and market listener thread
class FxLocalALE(ILearningEnvironment):

    def __init__(self, db_path, window_wid, rng):
        # fields
        self._window_wid = window_wid
        # set to zeros
        self._time_pointer = 0
        self._game_over = False
        self._rng = rng
        # init
        self._connect_fx_db_(db_path)
        self._check_time_periods_()
        self._read_time_intervals_()

    def _connect_fx_db_(self, db_path):
        self.db = SqliteConnector()
        self.db.connect(db_path)

    def _check_time_periods_(self):
        table_names = self.db.get_tables()
        base_time_column = []
        base_table_name = ''

        if not len(table_names):
            raise Exception("Empty Database")

        # columns - 1 (time column) cross tables amount (should be conformable)
        self._data_len = (len(self.db.get_table_columns(table_names[0])) - 1) * len(table_names)

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
                    raise Exception("tables \'" + base_table_name + "\' and \'" + table_name + "\' are not conformable")

    def _read_time_intervals_(self):
        table_names = self.db.get_tables()

        # read time from the first table (table index doesn't matter, if _check_time_periods_ has been passed)
        time_column = self.db.read_table_column(table_names[0], 'time', 1)
        self._time_ticks = len(time_column)
        session_vector = np.zeros((self._time_ticks, 1))

        np_time_vector = np.array(time_column).reshape((self._time_ticks, 1))
        time_diff = np.diff(np_time_vector[:, 0])
        print time_diff

        # find base (minimal) period of data changing (MS, SEC, MIN...)
        self._period = np.min(time_diff)

        # working session
        ea_session = EASession()

        # find all periods larger than base period
        time_diff -= self._period
        break_points, = np.nonzero(time_diff)
        time_sessions = []
        start_id = 0
        for bp in break_points.tolist():
            end_id = bp
            time_sessions += ea_session.extract_from_time_ids(time_column, start_id, end_id, self._period)
            start_id = bp + 1
        end_id = len(time_column) - 1
        time_sessions += ea_session.extract_from_time_ids(time_column, start_id, end_id, self._period)

        for session in time_sessions:
            # DEBUG
            # interval_ms = UTCTimeIntervals(self._time_column[session[0]], self._time_column[session[1]])
            # print_utc_time_interval(interval_ms)
            session_vector[session[0]:(session[1] + 1)] = 1

        self._time_matrix = np.concatenate((np_time_vector, session_vector), 1)

        # DEBUG
        for i in range(self._time_ticks):
           print utc_ms_to_str(self._time_matrix[i, 0]), "session:", self._time_matrix[i, 1]

    def load_tge_from_json(self, json):
        pass

    def act(self, action):
        if self._time_pointer < self._time_ticks - 1:
            self._time_pointer += 1
        else:
            self._time_pointer = 0
            self._game_over = True

    def game_over(self):
        return self._game_over

    def reset_game(self):
        self._game_over = False

    def getMinimalActionSet(self):
        pass

    def getScreenDims(self):
        return self._data_len, int(self._window_wid / self._period)

    def lives(self):
        pass

    # convert wide window to short window
    def getScreenGrayscale(self, screen_buffer):
        self.fillBuffer(screen_buffer)

    def fillBuffer(self, screen_buffer):
        (h, w) = screen_buffer.shape
        assert h == self._data_len and w == int(self._window_wid / self._period)
        '''
        screen_buffer[:, :] = self.db.read_tables_rows(
                "time",
               self._time_pointer,
               self._time_pointer - (self._window_wid_in_period - 1) * self._period,
               ["time"]
        )
        '''
