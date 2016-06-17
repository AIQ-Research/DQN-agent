__author__ = 'vicident'

from gym import Env
from gym.spaces import Discrete, Tuple, Box
import pandas as pd
import sqlite3
import numpy as np
from enum import Enum
import logging
from fx_session import MarketSession

class Order(Enum):
    NONE = 0
    BUY = 1
    SELL = 2
    CLOSE = 3

class FxVerySimpleAccount(object):

    def __init__(self, margin, contract):
        self.margin = margin
        self.spot = 0
        self.order = Order.NONE
        self.contract = contract

    def buy(self, price_bid):
        if self.order == Order.NONE:
            self.spot = price_bid
            self.order = Order.BUY

    def sell(self, price_ask):
        if self.order == Order.NONE:
            self.spot = price_ask
            self.order = Order.SELL

    def close_order(self, price):
        if self.order == Order.BUY:
            reward = (price - self.spot - self.margin) * self.contract
            logging.debug("BUY: %f, SELL: %f, Margin: %f, Contract: %d, REWARD: %d" % (self.spot, price, self.margin, self.contract, reward))
        elif self.order == Order.SELL:
            reward = (self.spot - price - self.margin) * self.contract
            logging.debug("BUY: %f, SELL: %f, Margin: %f, Contract: %d, REWARD: %d" % (price, self.spot, self.margin, self.contract, reward))
        else:
            reward = 0.0
        self.order = Order.NONE
        return reward


class FxTrader(Env):

    def __init__(self, base_path, pair_name, session, window_size, pip_margin, contract):
        self.session = session
        # load all tables in dictionary of data frames (pandas)
        self.db, self.tables_dict, self.data_len, self.frame_w = self.__load_tables(base_path, pair_name)
        self.frame_len = window_size
        self.db_pointer = self.frame_len
        # variables for gym Env
        self.observation_space = Box(low=-contract, high=contract, shape=(self.frame_len, self.frame_w))
        self.reward_range = (-contract, contract)
        self.action_space = Discrete(4)
        self.viewer = None
        # Forex emulator
        self.fx_account = FxVerySimpleAccount(pip_margin, contract)
        print "Total ticks:", self.data_len, ", frame ticks:", self.frame_len, ", data width:", self.frame_w

    def _close(self):
        pass

    def _step(self, action):
        """
        :param action:
        :return: observation, reward, game_over, comments
        """
        next_frame, price, volume, new_session = self.__get_frame()
        self.db_pointer += self.frame_len

        reward = 0

        if Order(action) == Order.CLOSE:
            reward = self.fx_account.close_order(price)
        elif Order(action) == Order.BUY:
            self.fx_account.buy(price)
        elif Order(action) == Order.SELL:
            self.fx_account.sell(price)

        game_over = new_session

        return next_frame, reward, game_over, {}

    def _reset(self):
        next_frame, price, volume, new_session = self.__get_frame()
        return next_frame

    def _render(self, mode='human', close=False):
        if close:
            return

    def _configure(self):
        pass

    def _seed(self, seed=None):
        return [1, 2, 3]

    def __load_tables(self, db_path, pair_name):
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

        # TODO: check correctness
        df = pd.concat(df_list, axis=1)
        df.columns = table_names

        tables_dict = dict(zip(table_names, range(len(table_names))))
        h, w = df.shape
        return df, tables_dict, h, w - 1

    def __rewind(self):
        rewinding = True
        new_session = False
        while rewinding:
            self.db_pointer += 1
            # check new cycle
            if self.db_pointer >= self.data_len:
                self.db_pointer = self.frame_len
                new_session = True
            time_point_ms = self.db.iloc[self.db_pointer, self.tables_dict["time"]]
            # get current day
            day = MarketSession.ms_to_datetime(time_point_ms)
            # get session range for current day
            begin_ms, end_ms = self.session.get_session_range(day)
            # come session
            if begin_ms <= time_point_ms < end_ms:
                rewinding = False
            else:
                rewinding = True
                new_session = True

        return new_session

    def __get_frame(self):
        # rewind self.db_pointer to nearest pre-defined market session
        new_session = self.__rewind()
        frame = self.db[(self.db_pointer - self.frame_len):self.db_pointer]
        frame_data_only = frame.drop(['time'], axis=1)
        # return dataframe, last CLOSE PRICE from dataframe, last VOLUME from dataframe
        return frame_data_only.as_matrix(), \
                frame.iloc[-1, self.tables_dict["CLOSE_PRICE"]], \
                frame.iloc[-1, self.tables_dict["VOLUME"]], \
                new_session

    def print_time_pointer(self):
        time_point_ms = self.db.iloc[self.db_pointer, self.tables_dict["time"]]
        print MarketSession.ms_to_datetime(time_point_ms)

    def get_frame(self):
        return self.__get_frame()