__author__ = 'vicident'


from gym import envs
from fx_traider import FxTrader
#env = envs.make("SpaceInvaders-v0")
import logging, sys
from fx_network import fx_cnn_v0, fx_cnn_v1

root = logging.getLogger()
root.setLevel(logging.INFO)

my_env = FxTrader("/Users/vicident/Development/hdata/fxpairs2014.db", "EUR_USD", 288, 0.002, 100000)

import kerlym

agent = kerlym.agents.D2QN(
                    my_env,
                    nframes=1,
                    epsilon=0.5,
                    discount=0.99,
                    modelfactory=fx_cnn_v1,
                    update_nsamp=10,
                    batch_size=1,
                    dropout=0.1,
                    enable_plots = True,
                    max_memory = 2880,
                    epsilon_schedule=lambda episode,epsilon: max(0.1, epsilon*(1-1e-4)),
                    dufference_obs = True,
                    preprocessor = None,
                    learning_rate = 1e-3
                    )
agent.learn()