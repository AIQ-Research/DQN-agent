__author__ = 'vicident'

from fx_order import BuyOrder, SellOrder
import pandas as pd
import sqlite3

import logging
from fx_session import MarketSession
from calendar import monthrange


class FxBroker:

    def __init__(self, db_folder, pair_name, session):
        self.db, self.tables, self.sessions = self.__load_tables("/".join([db_folder, "fxpairs2014.db"]), pair_name, session)
        self.sessions_num = len(self.sessions)
        self.session_len = max([b-a for a, b in self.sessions])
        logging.info("max session length: {0}".format(self.session_len))
        self.db_pointer = 0
        self.session_pointer = 0

    def __load_tables(self, db_path, pair_name, session):
        """
        :param db_path: path to historical data
        :param pair_name: name of currency exchange pair
        :return:
        """
        # connect to sqlite database
        con = sqlite3.connect(db_path)
        # fetch table names
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        cdata = cursor.fetchall()
        table_names = [c[0] for c in cdata]
        # read tables data to data frames (pandas)
        df_list = [pd.read_sql_query("SELECT time from " + table_names[0], con)]
        for name in table_names:
            df_list.append(pd.read_sql_query("SELECT " + pair_name + " from " + name, con))
        con.close()
        table_names = ["time"] + table_names

        df = pd.concat(df_list, axis=1)
        df.columns = table_names

        tables_dict = dict(zip(table_names, range(len(table_names))))

        stop = False
        base_pointer = 0
        sessions = []
        while not stop:
            time_point_ms = df.ix[base_pointer, 'time']
            # get current day
            day = MarketSession.ms_to_datetime(time_point_ms)
            # get session's time limits for current day
            begin_ms, end_ms = session.get_session_range(day)
            # find time limits in database
            begin_ids = df[df['time'] == begin_ms].index.tolist()
            end_ids = df[df['time'] == end_ms + 1].index.tolist()
            # there should be only single time point per each limit
            if len(begin_ids) == 1 and len(end_ids) == 1:
                interval_len = end_ids[0] - begin_ids[0]
                volumes = df.ix[(interval_len/4 + begin_ids[0]):(3*interval_len/4 + begin_ids[0]), 'VOLUME']
                prices = df.ix[(interval_len/4 + begin_ids[0]):(3*interval_len/4 + begin_ids[0]), 'CLOSE_PRICE']
                # check real trading activity
                if volumes.sum() and prices.max() != prices.min():
                    sessions.append((begin_ids[0], end_ids[0] - 1))

            _, max_days = monthrange(day.year, day.month)

            for i in xrange(1, max_days + 1):
                next_point_ids = df[df['time'] == begin_ms + session.get_session_period()*i].index.tolist()
                if len(next_point_ids) == 1:
                    base_pointer = next_point_ids[0]
                    stop = False
                    break
                else:
                    stop = True

        return df, tables_dict, sessions

    def _next_random_session(self, seed, frame_len):
        start_session = frame_len / self.session_len + 1
        self.session_pointer = seed % self.sessions_num
        if self.session_pointer < start_session:
            self.session_pointer = start_session
        logging.info("go to random session: {0}".format(self.session_pointer))
        self.db_pointer = self.sessions[self.session_pointer][0]

    def _next_session(self, frame_len):
        start_session = frame_len / self.session_len + 1
        if self.session_pointer < self.sessions_num - 1:
            self.session_pointer += 1
        else:
            self.session_pointer = start_session
        self.db_pointer = self.sessions[self.session_pointer][0]

    def _first_session(self, frame_len):
        start_session = frame_len / self.session_len + 1
        self.session_pointer = start_session
        self.db_pointer = self.sessions[self.session_pointer][0]

    def _next_frame(self):
        if self.db_pointer < self.sessions[self.session_pointer][1] - 1:
            self.db_pointer += 1
            last_frame_flag = False
        else:
            last_frame_flag = True

        return last_frame_flag

    def _get_frame(self, frame_len):
        frame = self.db[(self.db_pointer - frame_len):self.db_pointer]
        return frame

    def get_frame_width(self):
        return len(self.tables)

    def get_sessions_num(self):
        return len(self.sessions)


class FxBroker2orders(FxBroker):

    def __init__(self, db_folder, pair_name, session, balance, lot, sl, tp):
        FxBroker.__init__(self, db_folder, pair_name, session)
        self.balance = balance
        self.sl = sl
        self.tp = tp
        self.lot = lot
        self.buy_order = None
        self.sell_order = None
        self.init = False
        self.actions = {
            0: self.__nop,
            1: self.__buy,
            2: self.__sell
        }

    def __nop(self, spot_price):
        pass

    def __buy(self, spot_price):
        if self.buy_order is None:
            self.buy_order = BuyOrder(spot_price, self.lot, self.sl, self.tp)
            self.balance -= self.lot

    def __sell(self, spot_price):
        if self.sell_order in None:
            self.sell_order = SellOrder(spot_price, self.lot, self.sl, self.tp)
            self.balance -= self.lot

    def __step(self, frame_len, seed):
        if not self.init:
            self._first_session(frame_len)
            self.init = True
        frame = self._get_frame(frame_len)
        last_frame = self._next_frame()

        if last_frame:
            self._next_random_session(frame_len, seed)

        return frame, last_frame

    def reset(self, frame_len, seed):
        self._next_random_session(seed, frame_len)
        return self._get_frame(frame_len)

    def step(self, action, frame_len, seed):
        frame, last_frame = self.__step(frame_len, seed)

        spot_price = frame.ix[-1, 'CLOSE_PRICE']

        total_reward = 0
        total_equity = self.balance

        if self.buy_order is not None:
            equity, reward, closed = self.buy_order.step(spot_price)
            if closed:
                self.buy_order = None
                self.balance += equity
            total_reward += reward
            total_equity += equity

        if self.sell_order is not None:
            equity, reward, closed = self.sell_order.step(spot_price)
            if closed:
                self.sell_order = None
                self.balance += equity
            total_reward += reward
            total_equity += equity

        self.actions[action](spot_price)

        return frame, total_reward, last_frame

    def get_balance(self):
        return self.balance

    def get_actions_num(self):
        return len(self.actions.keys())