__author__ = 'vicident'

from gym import Env
from gym.spaces import Discrete, Box
import random

MAX_SEED = 1234567890


class FxTrader(Env):

    def __init__(self, window_size, broker, preprocessor):
        self.preprocessor = preprocessor
        self.broker = broker
        self.frame_len = window_size
        self.frame_width = self.broker.get_frame_width()
        self.game_over = True
        # variables for gym Env
        balance = broker.get_balance()
        min_value, max_value = self.preprocessor.get_range()
        actions_num = broker.get_actions_num()
        self.observation_space = Box(low=min_value, high=max_value, shape=(self.frame_len, self.frame_width))
        self.reward_range = (-balance, balance)
        self.action_space = Discrete(actions_num)
        self.viewer = None
        print "Total sessions:", self.broker.get_sessions_num(), ", frame ticks:", self.frame_len, ", data width:", self.frame_width

    def _step(self, action):
        """
        :param action:
        :return: observation, reward, game_over, comments
        """
        next_frame, reward, self.game_over = self.broker.step(action, self.frame_len, self.seed())
        if self.game_over:
            self.preprocessor.init(next_frame)
        prep_frame = self.preprocessor.process(next_frame)
        return prep_frame, reward, self.game_over, {}

    def _reset(self):
        return self.broker.reset(self.frame_len, self.seed())

    def _render(self, mode='human', close=False):
        if close:
            return

    def _configure(self):
        pass

    def _seed(self, seed=None):
        return random.randint(1, MAX_SEED)
