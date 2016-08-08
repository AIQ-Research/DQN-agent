__author__ = 'vicident'

import logging
from sandbox.fx_strategy import FxStrategyTestBroker
from sandbox.fx_session import EASession

root = logging.getLogger()
root.setLevel(logging.DEBUG)


if __name__ == "__main__":
    my_strategy = FxStrategyTestBroker(db_folder='',
                            db_list=[],
                            frame_len=120,
                            pair_name='AUD_USD',
                            session=EASession(),
                            start_volume=100000,
                            lot=10000,
                            sl_rate=0.01,
                            tp_rate=0.03,
                            lose_rate=0.98,
                            slippage=0.005)

    for i in xrange(2000):
        my_strategy.step(-1, -1)
