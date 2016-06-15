__author__ = 'vicident'


from gym import envs
#from fx_traider import FxTrader
import fx_trader
#env = envs.make("SpaceInvaders-v0")
import logging, sys
from fx_network import fx_dnn_v0, fx_rnn_v0

root = logging.getLogger()
root.setLevel(logging.INFO)

#my_env = FxTrader("/home/vicident/Development/data/fxpairs2014.db", "EUR_USD", 288, 0.002, 100000)
from gym.envs.registration import register
register(
    id='Fxtrader-v0',
    entry_point='fx_trader:FxTrader',
    kwargs={'base_path':'/home/vicident/Development/data/fxpairs2014.db', 'pair_name':'EUR_USD', 'window_size':120, 'pip_margin':0.002, 'contract':100000},
    timestep_limit=200,
    reward_threshold=0.99, # optimum = 1
)

import kerlym

agent = kerlym.agents.DQN(
		    "Fxtrader-v0",
		    nthreads=4,
                    nframes=1,
                    epsilon=0.5,
                    discount=0.99,
                    modelfactory=fx_rnn_v0,
                    update_nsamp=10,
                    batch_size=32,
                    dropout=0.5,
                    enable_plots = False,
                    max_memory = 12000,
                    epsilon_schedule=lambda episode,epsilon: max(0.1, epsilon*(1-1e-4)),
                    dufference_obs = True,
                    preprocessor = None
                    )
agent.train()
