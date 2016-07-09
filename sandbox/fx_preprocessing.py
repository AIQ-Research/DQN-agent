__author__ = 'vicident'

import logging


class FxPreprocessing:

    def __init__(self):
        self.init_flag = False

    def init(self, data_frame):
        self.init_flag = True
        return self._init(data_frame)

    def process(self, data_frame):
        if not self.init_flag:
            self.init(data_frame)

        return self._process(data_frame)

    def get_range(self):
        return self._get_range()

    def _init(self, data_frame):
        raise NotImplementedError

    def _process(self, data_frame):
        raise NotImplementedError

    def _get_range(self):
        raise NotImplementedError


class FxSimpleNormalization(FxPreprocessing):

    def __init__(self, border_gap=0.1):
        self.border_gap = border_gap
        FxPreprocessing.__init__(self)

    def _init(self, data_frame):
        self.min_value = data_frame.min(axis=0)*(1 - self.border_gap)
        max_value = data_frame.max(axis=0)*(1 + self.border_gap)
        # (value - min_value)/(max_value - min_value)
        self.divider = max_value - self.min_value
        #logging.debug("min_value = {0}, divider = {1}".format(self.min_value, self.divider))

    def _process(self, data_frame):
        sub = data_frame.sub(self.min_value, axis='columns')
        div = sub.div(self.divider, axis='columns')
        res = div.ix[:, ['OPEN_PRICE', 'MIN_PRICE', 'MAX_PRICE', 'CLOSE_PRICE', 'VOLUME']].as_matrix()
        return res

    def _get_range(self):
        return 0.0, 1.0
