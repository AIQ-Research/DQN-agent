__author__ = 'vicident'

import logging
from sandbox.fx_network import fx_dnn_v0, fx_rnn_v0
from sandbox.fx_strategy import FxStrategyTwoOrders
from sandbox.fx_preprocessing import FxSimpleNormalization
from sandbox.fx_session import EASession

root = logging.getLogger()
root.setLevel(logging.DEBUG)

#"/home/vicident/Development/data/fxpairs2014.db"
#'/Users/vicident/Development/hdata/fxpairs2014.db'
from gym.envs.registration import register

my_strategy = FxStrategyTwoOrders(db_folder='/Users/vicident/Development/hdata/',
                            db_list=["fxpairs2013.db"],
                            frame_len=120,
                            pair_name='AUD_USD',
                            session=EASession(),
                            start_volume=100000,
                            lot=10000,
                            sl_rate=0.01,
                            tp_rate=0.03,
                            lose_rate=0.98,
                            slippage=0.005)

my_preprocessor = FxSimpleNormalization(border_gap=0.2)

register(
    id='Fxtrader-v0',
    entry_point='fx_trader:FxTrader',
    kwargs={'window_size': 120, 'strategy': my_strategy, 'preprocessor': my_preprocessor},
    timestep_limit=200,
    reward_threshold=0.99,  # optimum = 1
)

import kerlym

agent = kerlym.agents.DQN(
                    "Fxtrader-v0",
                    nthreads=1,
                    nframes=1,
                    epsilon=0.5,
                    discount=0.99,
                    modelfactory=fx_rnn_v0,
                    update_nsamp=10,
                    batch_size=32,
                    dropout=0.5,
                    enable_plots=False,
                    max_memory=12000,
                    epsilon_schedule=lambda episode,epsilon: max(0.1, epsilon*(1-1e-4)),
                    dufference_obs=True,
                    preprocessor=None
                    )
agent.train()
