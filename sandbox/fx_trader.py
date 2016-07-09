__author__ = 'vicident'

from gym import Env
from gym.spaces import Discrete, Box
import random
import logging


MAX_SEED = 1234567890


class FxTrader(Env):

    def __init__(self, window_size, strategy, preprocessor):
        self.preprocessor = preprocessor
        self.strategy = strategy
        self.frame_len = window_size
        self.frame_width = self.strategy.get_frame_width() - 1
        # variables for gym Env
        balance = strategy.get_balance()
        min_value, max_value = self.preprocessor.get_range()
        actions_num = strategy.get_actions_num()
        self.observation_space = Box(low=min_value, high=max_value, shape=(self.frame_len, self.frame_width))
        self.reward_range = (-balance, balance)
        self.action_space = Discrete(actions_num)
        self.viewer = None
        print "Total sessions:", self.strategy.get_sessions_num(), ", frame ticks:", self.frame_len, ", data width:", self.frame_width

    def _step(self, action):
        next_frame, reward, game_over, session_over = self.strategy.step(action, self.seed())

        if session_over or game_over:
            self.preprocessor.init(next_frame)

        prep_frame = self.preprocessor.process(next_frame)
        return prep_frame, reward, game_over, {}

    def _reset(self):
        next_frame = self.strategy.reset(self.seed())
        return self.preprocessor.process(next_frame)

    def _render(self, mode='human', close=False):
        if close:
            return

    def _configure(self):
        pass

    def _seed(self, seed=None):
        return random.randint(1, MAX_SEED)
