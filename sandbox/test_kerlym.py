__author__ = 'vicident'

import logging
from fx_network import fx_dnn_v0, fx_rnn_v0
from fx_broker import FxBroker2orders
from fx_preprocessing import FxSimpleNormalization
from fx_session import EASession

root = logging.getLogger()
root.setLevel(logging.INFO)

#"/home/vicident/Development/data/fxpairs2014.db"
#'/Users/vicident/Development/hdata/fxpairs2014.db'
from gym.envs.registration import register

my_broker = FxBroker2orders(db_folder='/Users/vicident/Development/hdata/',
                            pair_name='EUR_USD',
                            session=EASession(),
                            balance=100000,
                            lot=10000,
                            sl=0.1,
                            tp=0.3)

my_preprocessor = FxSimpleNormalization(border_gap=0.2)

register(
    id='Fxtrader-v0',
    entry_point='fx_trader:FxTrader',
    kwargs={'window_size': 120, 'broker': my_broker, 'preprocessor': my_preprocessor},
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
