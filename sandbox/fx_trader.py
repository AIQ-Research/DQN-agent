__author__ = 'vicident'

from gym import Env
from gym.spaces import Discrete, Tuple, Box
import pandas as pd
import sqlite3
import numpy as np
from enum import Enum
import logging

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

    def __init__(self, base_path, pair_name, window_size, pip_margin, contract):
        # actions: 'buy', 'sell', 'do nothing'
        self.action_space = Discrete(4)
        # load all tables in dictionary of data frames (pandas)
        self.db, self.tables_dict, self.data_len, self.frame_w = self.__load_tables(base_path, pair_name)
        self.frame_len = window_size
        self.observation_space = Box(low=-contract, high=contract, shape=(self.frame_len, self.frame_w))
	self.reward_range = (-contract, contract)
        self.viewer = None
        self.db_pointer = self.frame_len
        self.fx_account = FxVerySimpleAccount(pip_margin, contract)
        print "Total ticks:", self.data_len, ", frame ticks:", self.frame_len, ", data width:", self.frame_w
	print self.__get_frame()

    def _close(self):
        pass

    def _step(self, action):
        """
        :param action:
        :return: observation, reward, game_over, comments
        """
        next_frame, price, volume = self.__get_frame()
        self.db_pointer += self.frame_len

        reward = 0

        if Order(action) == Order.CLOSE:
            reward = self.fx_account.close_order(price)
        elif Order(action) == Order.BUY:
            self.fx_account.buy(price)
        elif Order(action) == Order.SELL:
            self.fx_account.sell(price)

        game_over = volume == 0.0

        if self.db_pointer >= self.data_len:
            self.db_pointer = self.frame_len
            game_over = True

        return next_frame, reward, game_over, {}

    def _reset(self):
        next_frame, price, volume = self.__get_frame()
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
        :param db_path:
        :param pair_name:
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
        df_list = [pd.read_sql_query("SELECT time from " +  table_names[0], con)]
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
	pass

    def __get_frame(self):
	# rewind self.db_pointer to nearest pre-defined market session
	self.__rewind()
        frame = self.db[(self.db_pointer - self.frame_len):self.db_pointer]
        return frame.as_matrix(), \
               frame.iloc[-1, self.tables_dict["CLOSE_PRICE"]], \
               frame.iloc[-1, self.tables_dict["VOLUME"]]
