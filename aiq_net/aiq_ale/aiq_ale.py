__author__ = 'vicident'

from aiq_net.interfaces.ile import ILearningEnvironment
from aiq_net.interfaces.iagent import IAgent
from Queue import Queue
from threading import Lock
from aiq_net.aiq_define import DEFAULT_START_REWARD
from aiq_net.aiq_db.connectors import SqliteConnector

import numpy as np

# Two active threads meet here: trainer thread and market listener thread
class FxLocalALE(ILearningEnvironment):

    def __init__(self, db_path):
        self._connect_fx_db_(db_path)
        self._check_time_periods_()

    def _connect_fx_db_(self, db_path):
        self.db = SqliteConnector()
        self.db.connect(db_path)

    def _check_time_periods_(self):
        table_names = self.db.get_tables()
        base_time_column = []
        base_table_name = ''

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

    def load_tge_from_json(self, json):
        pass

    def act(self, action):
        pass

    def game_over(self):
        pass

    def reset_game(self):
        # we can't control the market
        pass

    def getMinimalActionSet(self): pass

    def getScreenDims(self): pass

    def lives(self): pass

    def getScreenGrayscale(self, screen_buffer):
        pass
        # copy actual frame to buffer
        #np.copyto(screen_buffer, self.observation)
