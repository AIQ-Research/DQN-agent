__author__ = 'vicident'

from aiq_net.interfaces.ile import ILearningEnvironment
from aiq_net.aiq_db.connectors import SqliteConnector
import numpy as np
from matplotlib import mlab

from aiq_fx import UTCTimeIntervals, print_utc_time_interval, EASession, utc_ms_to_str, SessionPreprocessing


# Two active threads meet here: trainer thread and market listener thread
class FxLocalALE(ILearningEnvironment):

    def __init__(self, db_path, image_wid, periods_list, rng):
        # fields
        self._periods_list = periods_list
        self._image_wid = image_wid
        self._window_wid = np.max(self._periods_list) * self._image_wid
        self._rng = rng
        self._columns_include = ["EUR_GBP"]
        # set to zeros
        self._time_pointer = 0
        self._begin_pointer = 0
        self._game_over = False
        self._first_frame = True
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
        self._data_wid = len(table_names) * len(self._columns_include)

        # read time from the first table (table index doesn't matter, if _check_time_periods_ has been passed)
        time_column = self.db.read_table_column(table_names[0], 'time', 1)
        self._time_ticks = len(time_column)
        session_vector = np.zeros((self._time_ticks, 1))

        np_time_vector = np.array(time_column).reshape((self._time_ticks, 1))
        time_diff = np.diff(np_time_vector[:, 0])

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
        # for i in range(self._time_ticks):
        #   print utc_ms_to_str(self._time_matrix[i, 0]), "session:", self._time_matrix[i, 1]

        self._begin_pointer = self._window_wid
        self._time_pointer = self._begin_pointer
        self.__rewind_to_session()

    def load_tge_from_json(self, json):
        pass

    # make an action
    def __act(self):
        return 0

    # stop the game at the last moment of the session
    def __finalize(self):
        return 0

    # rewind to the next playing time
    def __rewind_to_session(self):
        # rewind until end of the year
        while not self._time_matrix[self._time_pointer, 1] and self._time_pointer < (self._time_ticks - 1):
            self._time_pointer += 1
        # rewind until begin of the year
        if self._time_pointer == self._time_ticks - 1:
            self._time_pointer = self._begin_pointer
            while not self._time_matrix[self._time_pointer, 1]:
                self._time_pointer += 1
        self._first_frame = True

    def act(self, action):
        reward = 0
        if not self._time_matrix[self._time_pointer, 1]:
            self._game_over = True
            self.__rewind_to_session()
        else:
            # play the game
            reward = self.__act()

            if self._time_pointer < self._time_ticks - 1:
                self._time_pointer += 1
            else:
                self._time_pointer = self._begin_pointer
                self.__rewind_to_session()
                self._game_over = True

        if self._game_over:
            reward = self.__finalize()

        return reward

    def game_over(self):
        return self._game_over

    def reset_game(self):
        self._game_over = False

    def getMinimalActionSet(self):
        pass

    def getScreenDims(self):
        return self._image_wid, self._image_wid

    def lives(self):
        pass

    # convert wide window to short window
    def getScreenGrayscale(self, screen_buffer):
        self.__fill_buffer(screen_buffer)

    @staticmethod
    def movingaverage (values, window):
        weights = np.repeat(1.0, window)/window
        sma = np.convolve(values, weights, 'valid')
        return sma

    def __preprocess_signal(self, buffer):
        if self._first_frame:
            self._session_prep = SessionPreprocessing(buffer)
        buffer_prep = self._session_prep.process(buffer)
        print buffer_prep
        h, w = buffer_prep.shape
        base = self._image_wid
        frame = np.zeros((base, base, h), np.float32)
        p = len(self._periods_list)
        ps = base / p
        for i in range(h):
            cnt = 0
            for j in self._periods_list:
                cnt += 1
                sma = self.movingaverage(buffer_prep[i, :], j)
                frame[(cnt-1)*ps:cnt*ps, :, i] = sma[0:j*base:j]
        return frame

    def __fill_buffer(self, screen_buffer):
        h, w = screen_buffer.shape
        assert h == self._image_wid and w == self._image_wid

        fx_buffer = self.db.read_tables_rows(
                "time",
               self._time_matrix[self._time_pointer - self._window_wid + 1, 0],
               self._time_matrix[self._time_pointer, 0],
               self._columns_include
        )

        buffer_prep = self.__preprocess_signal(fx_buffer)
        screen_buffer[:, :] = buffer_prep[:, :, -1]
