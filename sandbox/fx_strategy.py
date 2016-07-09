__author__ = 'vicident'

import abc
from fx_broker import FxSingleCurrencyBroker
import logging


class FxStrategyBase(object):
    ___metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def step(self, action, seed):
        return NotImplemented

    @abc.abstractmethod
    def get_actions_num(self):
        return NotImplemented

    @abc.abstractmethod
    def reset(self, seed):
        return NotImplemented


class FxStrategyTwoOrders(FxStrategyBase, FxSingleCurrencyBroker):

    def __init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume, lot,
                 sl_rate=0.01, tp_rate=0.03, lose_rate=0.5, slippage=0.005):

        FxSingleCurrencyBroker.__init__(self, db_folder, db_list, pair_name, session, start_volume, slippage)
        self.frame_len = frame_len
        self.sl_rate = sl_rate
        self.tp_rate = tp_rate
        self.lose_rate = lose_rate
        self.lot = lot
        self.actions = {
            0: self.__nop,
            1: self.__buy,
            2: self.__sell
        }
        self._go_first_session(self.frame_len)

    def __nop(self):
        pass

    def __buy(self):
        self._add_order(FxSingleCurrencyBroker.BUY_ORDER, self.lot, self.sl_rate, self.tp_rate)

    def __sell(self):
        self._add_order(FxSingleCurrencyBroker.SELL_ORDER, self.lot, self.sl_rate, self.tp_rate)

    def reset(self, seed):
        self._reset()
        self._go_next_random_session(seed, self.frame_len)
        return self._get_frame(self.frame_len)

    def step(self, action, seed):
        frame = self._get_frame(self.frame_len)
        session_over = self._go_next_frame()
        reward = self.update_orders(session_over)

        if session_over:
            balance = self.get_balance()
            logging.debug("session has been closed with the balance = " + str(balance))

        # game is over if we have lost a much
        game_over = float(self.get_equity()) / float(self.get_start_balance()) < self.lose_rate

        # make an action if continue playing
        if not game_over:
            self.actions[action]()
        else:
            reward = self.update_orders(True)
        # go to next session
        if session_over and not game_over:
            self._go_next_random_session(seed, self.frame_len)

        return frame, reward, game_over, session_over

    def get_actions_num(self):
        return len(self.actions.keys())


class FxStrategyRollover(FxStrategyBase, FxSingleCurrencyBroker):
    def __init__(self, db_folder, db_list, frame_len, pair_name, session, start_volume, slippage=0.05):
        FxSingleCurrencyBroker.__init__(self, db_folder, db_list, pair_name, session, start_volume, slippage)
