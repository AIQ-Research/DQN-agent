__author__ = 'vicident'
__copyright__ = "Copyright 2016, AIQ-Research"
__credits__ = ["Denis Timoshenko"]
__license__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Denis Timoshenko"
__email__ = "tnediciv@gmail.com"
__status__ = "Prototype"

import operator
import pandas as pd
import sqlite3
from datetime import datetime
import pytz

import logging
from fx_session import MarketSession
from calendar import monthrange
import uuid

LONDON_TZ = pytz.timezone('Europe/London')
"""London's timezone for time output"""


class FxSingleCurrencyBroker(object):

    ORDERS_COLUMNS = ['TYPE', 'OPEN_TIME', 'OPEN_PRICE', 'VOLUME', 'SL_PRICE', 'TP_PRICE']
    """Table of orders"""
    SELL_ORDER = 1
    """Type definition of the sell order"""
    BUY_ORDER = -1
    """Type definition of the buy order"""
    DB_TABLES = {'TIME': 0, 'OPEN_PRICE': 1, 'MIN_PRICE': 2, 'MAX_PRICE': 3, 'CLOSE_PRICE': 4, 'VOLUME': 5}
    """Required tables of database"""

    def __init__(self, db_folder, db_list, pair_name, session, start_balance, slippage):
        """Constructor
        :param db_folder: folder contains databases
        :param db_list: list of databases' names
        :param pair_name: name of the trading currency pair
        :param session: market session for trading
        :param start_balance: start balance in volume units
        :param slippage: order's slippage (constant value)
        """
        data_frames_list = []
        self.sessions = []
        for db_name in db_list:
            db, sess = FxSingleCurrencyBroker.__load_tables("/".join([db_folder, db_name]), pair_name, session)
            data_frames_list.append(db)
            self.sessions += sess
        self.db = pd.concat(data_frames_list)
        self.sessions_num = len(self.sessions)
        self.session_len = max([b-a for a, b in self.sessions])
        logging.info("max session length: {0}".format(self.session_len))
        self.db_pointer = 0
        self.session_pointer = 0
        # fin data
        self.start_balance = start_balance
        self.orders_table = pd.DataFrame(columns=FxSingleCurrencyBroker.ORDERS_COLUMNS)
        self.balance = start_balance
        self.slippage = slippage

    @staticmethod
    def get_frame_width():
        """Return generated frame width
        :return: width of data frame
        """
        return len(FxSingleCurrencyBroker.DB_TABLES)

    def get_sessions_num(self):
        """Return number of available sessions
        :return: number of sessions
        """
        return len(self.sessions)

    def get_equity(self):
        """Return trader's equity
        :return: equity (as a volume of the base currency)
        """
        spot = self._get_spot()
        op_col = self.orders_table['OPEN_PRICE']
        sign_col = self.orders_table['TYPE']
        vol_col = self.orders_table['VOLUME']
        order_profits = ((op_col - spot).multiply(sign_col) + 1.0 - self.slippage).multiply(vol_col)

        return order_profits.sum() + self.balance

    def get_balance(self):
        """Return actual balance of the trader
        :return: actual balance (in volume units)
        """
        return self.balance

    def get_start_balance(self):
        """Return start balance of the trader
        :return: start balance (in volume units)
        """
        return self.start_balance

    def __update_orders(self, spot, orders_to_update):
        """
        :param spot:
        :param orders_to_update:
        :return:
        """
        op_col = orders_to_update['OPEN_PRICE']
        sign_col = orders_to_update['TYPE']
        vol_col = orders_to_update['VOLUME']
        orders_profits = (op_col - spot).multiply(sign_col) - self.slippage
        # profit given by orders
        profit_loss = orders_profits.multiply(vol_col).sum()

        self.orders_table = self.orders_table.drop(orders_to_update.index)
        self.balance += (orders_profits + 1.0).multiply(vol_col).sum()

        return profit_loss

    def update_orders(self, close):
        """Update state of orders
        :param close: close flag (force close all orders if True)
        :return: instant profit-loss of the orders, lists of indices of stop loss and take profit orders
        """
        spot = self._get_spot()
        profit_loss = 0

        if close:
            # close all
            logging.debug("market state:\n" + self.get_orders_snapshot().to_string())
            call_orders_sl = []
            call_orders_tp = []
            call_orders = self.orders_table
        else:
            # choose take profit and stop loss
            call_orders_sl_buy = self.orders_table[(self.orders_table['SL_PRICE'] >= spot) &
                                               (self.orders_table['TYPE'] == self.BUY_ORDER)]
            call_orders_sl_sell = self.orders_table[(self.orders_table['SL_PRICE'] <= spot) &
                                               (self.orders_table['TYPE'] == self.SELL_ORDER)]
            call_orders_sl = pd.concat([call_orders_sl_buy, call_orders_sl_sell])
            profit_loss += self.__update_orders(spot, call_orders_sl)

            call_orders_tp_buy = self.orders_table[(self.orders_table['TP_PRICE'] <= spot) &
                                                (self.orders_table['TYPE'] == self.BUY_ORDER)]
            call_orders_tp_sell = self.orders_table[(self.orders_table['TP_PRICE'] >= spot) &
                                                (self.orders_table['TYPE'] == self.SELL_ORDER)]
            call_orders_tp = pd.concat([call_orders_tp_buy, call_orders_tp_sell])
            profit_loss += self.__update_orders(spot, call_orders_tp)

        return profit_loss, call_orders_sl.index, call_orders_tp.index

    def get_orders_snapshot(self):
        """Return human-friendly instant snapshot of the orders table
        :return: pandas data frame of the orders
        """
        snapshot = self.orders_table.copy()
        for index, row in snapshot.iterrows():
            if row['TYPE'] == FxSingleCurrencyBroker.BUY_ORDER:
                snapshot['TYPE'].loc[index] = 'buy'
            elif row['TYPE'] == FxSingleCurrencyBroker.SELL_ORDER:
                snapshot['TYPE'].loc[index] = 'sell'
            sec = snapshot['OPEN_TIME'].loc[index] / 1000.0
            london_dt = LONDON_TZ.localize(datetime.utcfromtimestamp(sec), is_dst=None)
            snapshot['OPEN_TIME'].loc[index] = london_dt.strftime('%Y-%m-%d %H:%M')
        return snapshot

    def get_active_orders_num(self):
        """Return an amount of opened orders
        :return: opened orders count
        """
        return len(self.orders_table.index)

    def _reset(self):
        """Reset trading
        :return: final balance of previous trading period
        """
        final_balance = self.balance
        self.balance = self.start_balance
        self.orders_table = pd.DataFrame(columns=FxSingleCurrencyBroker.ORDERS_COLUMNS)
        return final_balance

    def _get_spot(self):
        """Return current spot price
        :return: instant spot price
        """
        return self.db.iloc[self.db_pointer, FxSingleCurrencyBroker.DB_TABLES['CLOSE_PRICE']]

    def _get_time(self):
        """Return current market time
        :return: instant market time
        """
        return self.db.iloc[self.db_pointer, FxSingleCurrencyBroker.DB_TABLES['TIME']]

    def _get_volume(self):
        """Return current volume of trading
        :return: instant volume of trading
        """
        return self.db.iloc[self.db_pointer, FxSingleCurrencyBroker.DB_TABLES['VOLUME']]

    def _add_order(self, order_type, lot, sl_rate, tp_rate):
        """Put order in orders table
        :param order_type: sell (FxSingleCurrencyBroker.SELL_ORDER) or buy (FxSingleCurrencyBroker.BUY_ORDER)
        :param lot: volume of the order
        :param sl_rate: stop-loss rate
        :param tp_rate: take-profit rate
        :return: index of created order (if accepted) or None (if declined)
        """
        if order_type not in [FxSingleCurrencyBroker.SELL_ORDER, FxSingleCurrencyBroker.BUY_ORDER]:
            raise AttributeError('incorrect type of order')

        # should have enough money on actual balance
        if lot <= self.balance:
            spot = self._get_spot()
            open_time = self._get_time()
            index = uuid.uuid4()
            if order_type == self.SELL_ORDER:
                self.orders_table.loc[index] = [order_type, open_time, spot, lot, spot*(1 + sl_rate), spot*(1 - tp_rate)]
            elif order_type == self.BUY_ORDER:
                self.orders_table.loc[index] = [order_type, open_time, spot, lot, spot*(1 - sl_rate), spot*(1 + tp_rate)]

            self.balance -= lot
            return index
        else:
            return None

    def _go_next_random_session(self, seed, frame_len):
        """Jump to the random session from available list of sessions
        :param seed: random generators output
        :param frame_len: length of the regression frame
        :return: new session pointer
        """
        start_session = frame_len / self.session_len + 1
        self.session_pointer = seed % self.sessions_num
        if self.session_pointer < start_session:
            self.session_pointer = start_session
        logging.info("go to random session: {0}".format(self.session_pointer))
        self.db_pointer = self.sessions[self.session_pointer][0]
        return self.session_pointer

    def _go_next_session(self, frame_len):
        """Jump to the next session
        :param frame_len: length of the regression frame
        :return: new session pointer
        """
        start_session = frame_len / self.session_len + 1
        if self.session_pointer < self.sessions_num - 1:
            self.session_pointer += 1
        else:
            self.session_pointer = start_session
        self.db_pointer = self.sessions[self.session_pointer][0]
        return self.session_pointer

    def _go_first_session(self, frame_len):
        """Jump to the first session
        :param frame_len: length of the regression frame
        :return: new session pointer
        """
        start_session = frame_len / self.session_len + 1
        self.session_pointer = start_session
        self.db_pointer = self.sessions[self.session_pointer][0]
        return self.session_pointer

    def _go_next_frame(self):
        """Move pointer to the next data frame (like a tick of the market)
        :return: True if current frame is the last frame in current session (False - otherwise)
        """
        if self.db_pointer < self.sessions[self.session_pointer][1] - 1:
            self.db_pointer += 1
            last_frame_flag = False
        else:
            last_frame_flag = True

        return last_frame_flag

    def _get_frame(self, frame_len):
        """Return current regression frame (current database point minus frame_len)
        :param frame_len:
        :return: regression frame with the shape (frame_len, self.get_frame_width())
        """
        frame = self.db[(self.db_pointer - frame_len):self.db_pointer]
        return frame

    @staticmethod
    def __load_tables(db_path, pair_name, session):
        """
        :param db_path: path to historical database
        :param pair_name: name of currency exchange pair
        :return: data frame of time, prices and volume, sessions list
        """
        table_names_pairs = sorted(FxSingleCurrencyBroker.DB_TABLES.items(), key=operator.itemgetter(1))
        logging.info("Loading " + db_path)
        # connect to sqlite database
        con = sqlite3.connect(db_path)
        # fetch table names
        cursor = con.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        cdata = cursor.fetchall()
        table_names = [c[0] for c in cdata]
        # check database
        for key, _ in table_names_pairs:
            if key not in table_names and key is not 'TIME':
                raise LookupError("Loaded database doesn't have required table: " + key)
        # read tables data to data frames (pandas)
        df_list = [pd.read_sql_query("SELECT TIME from " + table_names[0], con)]
        df_columns = []
        for key, _ in table_names_pairs:
            if key is not 'TIME':
                df_list.append(pd.read_sql_query("SELECT " + pair_name + " from " + key, con))
                logging.info(key + " has been read")
            df_columns.append(key)
        con.close()

        df = pd.concat(df_list, axis=1)
        df.columns = df_columns
        stop = False
        base_pointer = 0
        sessions = []
        while not stop:
            time_point_ms = df.ix[base_pointer, 'TIME']
            # get current day
            day = MarketSession.ms_to_datetime(time_point_ms)
            # get session's time limits for current day
            begin_ms, end_ms = session.get_session_range(day)
            # find time limits in database
            begin_ids = df[df['TIME'] == begin_ms].index.tolist()
            end_ids = df[df['TIME'] == end_ms + 1].index.tolist()
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
                next_point_ids = df[df['TIME'] == begin_ms + session.get_session_period()*i].index.tolist()
                if len(next_point_ids) == 1:
                    base_pointer = next_point_ids[0]
                    stop = False
                    break
                else:
                    stop = True

        return df, sessions
