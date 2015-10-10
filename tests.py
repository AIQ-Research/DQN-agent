__author__ = 'vicident'

from aiq_net import aiq_network, aiq_agent
from aiq_network import AIQLearner
from aiq_agent import AIQAgent

import numpy as np
from ale_data_set import floatX


def test_aiq_network():
    rng = np.random.RandomState(123456)
    net = aiq_network.AIQLearner(84, 84, 16, 4, .99, 0.95, .00025,
                                 .95, .95, 0.1, 10000, 32, 'linear', 'deepmind_rmsprop', 'sum', rng)

    print net, "has been created"


def test_aiq_agent():
    rng = np.random.RandomState(123456)

    net = AIQLearner(84, 84, 16, 4, .99, 0.95, .00025,
                     .95, .95, 0.1, 10000, 32, 'linear', 'deepmind_rmsprop', 'sum', rng)
    agent = AIQAgent(net, 0.1, 0.1, 0.1, 10000, "/tmp/", 0, 1, rng)
    observation = np.zeros((84, 84), dtype=floatX)

    agent.start_episode(observation)
    for i in xrange(100):
        agent.step(0, observation)
    agent.end_episode(0)

    print agent, 'has finished the GAME'


if __name__ == '__main__':
    test_aiq_agent()
