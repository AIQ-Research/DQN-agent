__author__ = 'vicident'

import abc
from fx_broker import FxSingleCurrencyBroker
import logging
import datetime

class FxStrategyBase(object):
    ___metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def step(self, action, seed):
        raise NotImplementedError

    @abc.abstractmethod
    def get_actions_num(self):
        raise NotImplementedError

    @abc.abstractmethod
    def reset(self, seed):
        raise NotImplementedError

    @abc.abstractmethod
    def strategy(self, action, sl_list_call, tp_list_call):
        raise NotImplementedError


class FxStrategySingleCurrency(FxStrategyBase, FxSingleCurrencyBroker):

    def __init__(self, db_folder, db_list, frame_len, pair_name, session,
                 start_volume, lot, sl_rate, tp_rate, lose_rate, slippage, lost_sum):

        FxSingleCurrencyBroker.__init__(self, db_folder, db_list, pair_name, session, start_volume, slippage,lost_sum)
        self.frame_len = frame_len
        self.sl_rate = sl_rate
        self.tp_rate = tp_rate
        self.lose_rate = lose_rate
        self.lot = lot
        self._go_first_session(self.frame_len)
        self.lost_sum=lost_sum

    def reset(self, seed):
        self._reset()
        self._go_next_random_session(seed, self.frame_len)
        return self._get_frame(self.frame_len)

    def step(self, action, seed):
        frame = self._get_frame(self.frame_len)
        session_over = self._go_next_frame()
        reward, sl_list_call, tp_list_call = self.update_orders(session_over)
        #logging.debug("sl_list_call: {0}".format(sl_list_call))
        #logging.debug("tp_list_call: {0}".format(tp_list_call))

        if session_over:
            balance = self.get_balance()
            logging.debug("session has been closed with the balance = " + str(balance))

        # game is over if we have lost a much
        game_over = float(self.get_equity()) / float(self.get_start_balance()) < self.lose_rate

        # make an action if continue playing
        if not game_over:
            self.strategy(action, sl_list_call, tp_list_call)
        else:
            reward, _, _ = self.update_orders(True)
        # go to next session
        if session_over and not game_over:
            self._go_next_random_session(seed, self.frame_len)

        return frame, reward, game_over, session_over


# Implementations


class FxStrategyTwoOrders(FxStrategySingleCurrency):

    def __init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume=100000,
                 lot=10000, sl_rate=0.02, tp_rate=0.06, lose_rate=0.5, slippage=0.005,lost_sum=0.0):

        FxStrategySingleCurrency.__init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume,
                                          lot, sl_rate, tp_rate, lose_rate, slippage,lost_sum)
        self.actions = {
            0: self.__nop,
            1: self.__buy,
            2: self.__sell
        }

    def __nop(self):
        return None

    def __buy(self):
        oid = self._add_order(FxSingleCurrencyBroker.BUY_ORDER, self.lot, self.sl_rate, self.tp_rate)
        return oid

    def __sell(self):
        oid = self._add_order(FxSingleCurrencyBroker.SELL_ORDER, self.lot, self.sl_rate, self.tp_rate)
        return oid

    def strategy(self, action, sl_list_call, tp_list_call):
        self.actions[action]()

    def get_actions_num(self):
        return len(self.actions.keys())


class FxStrategyRollover(FxStrategySingleCurrency):

    def __init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume=100000,
                 lot=10000, sl_rate=0.01, tp_rate=0.03, lose_rate=0.5, slippage=0.005, base_rate=0.01,lost_sum=0.0):

        FxStrategySingleCurrency.__init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume,
                                          lot, sl_rate, tp_rate, lose_rate, slippage,lost_sum)
        self.strategy_on = False
        self.base_rate = base_rate
        self.base_spot = self._get_spot()
        self.order = self.SELL_ORDER
        self.actions = {
            0: self.__nop,
            1: self.__turn_on,
            2: self.__turn_off
        }

    def __nop(self):
        pass

    def __turn_on(self):
        self.strategy_on = True

    def __turn_off(self):
        self.strategy_on = False

    def strategy(self, action, sl_list_call, tp_list_call):
        spot = self._get_spot()
        position_side=self._get_side_position()
        current_time =self._get_current_time()
        if not self.get_active_orders_num():
            pass


        # beginning of european and american session
        if current_time.hour()>=7 and current_time.hour()<19:
            self.lost_sum=self.lost_sum+(self.sl_rate+self.slippage)*self.lot
            self.lot= self.lost_sum+(1+ 0.01)/self.tp_rate

            if position_side == 2:
                    oid = self._add_order(FxSingleCurrencyBroker.BUY_ORDER, self.lot,  self.sl_rate,  self.tp_rate)
                    return  oid

    def get_actions_num(self):
        return len(self.actions.keys())


class FxStrategyTestBroker(FxStrategySingleCurrency):

    def __init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume=100000,
                 lot=10000, sl_rate=0.01, tp_rate=0.03, lose_rate=0.5, slippage=0.005, base_rate=0.01):

        FxStrategySingleCurrency.__init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume,
                                          lot, sl_rate, tp_rate, lose_rate, slippage)
        self.strategy_on = False
        self.base_rate = base_rate
        self.base_spot = self._get_spot()
        self.order = self.SELL_ORDER
        self.actions = {
            0: self.__buy,
            1: self.__sell
        }

    def __nop(self):
        pass

    def __buy(self):
        oid = self._add_order(FxSingleCurrencyBroker.BUY_ORDER, self.lot, self.sl_rate, self.tp_rate)
        return oid

    def __sell(self):
        oid = self._add_order(FxSingleCurrencyBroker.SELL_ORDER, self.lot, self.sl_rate, self.tp_rate)
        return oid

    def strategy(self, action, sl_list_call, tp_list_call):
        spot = self._get_spot()
        if spot == 1.0:
            self.actions[0]()
        else:
            self.actions[1]()

    def get_actions_num(self):
        return len(self.actions.keys())
