__author__ = 'vicident'

import aiq_define

from ale_agent import NeuralAgent
import aiq_data_set

class AIQAgent(NeuralAgent):

    def __init__(self, aiq_network, epsilon_start, epsilon_min,
                 epsilon_decay, replay_memory_size, exp_pref,
                 replay_start_size, update_frequency, rng):

        NeuralAgent.__init__(self, aiq_network, epsilon_start, epsilon_min,
                 epsilon_decay, replay_memory_size, exp_pref,
                 replay_start_size, update_frequency, rng)

        # Replace ale DataSet objects by FDataSet

        self.data_set = aiq_data_set.FDataSet(width=self.image_width,
                                             height=self.image_height,
                                             rng=rng,
                                             max_steps=self.replay_memory_size,
                                             phi_length=self.phi_length)

        self.test_data_set = aiq_data_set.FDataSet(width=self.image_width,
                                                  height=self.image_height,
                                                  rng=rng,
                                                  max_steps=self.phi_length * 2,
                                                  phi_length=self.phi_length)


if __name__ == "__main__":

    from aiq_network import AIQLearner
    import numpy as np
    from ale_data_set import floatX

    rng = np.random.RandomState(123456)

    net = AIQLearner(84, 84, 16, 4, .99, 0.95, .00025, .95, .95, 0.1, 10000, 32, 'linear', 'deepmind_rmsprop', 'sum', rng)
    agent = AIQAgent(net, 0.1, 0.1, 0.1, 10000, "/tmp/", 0, 1, rng)
    observation = np.zeros((84, 84), dtype=floatX)

    agent.start_episode(observation)
    for i in xrange(100):
        agent.step(0, observation)
    agent.end_episode(0)

    print agent, 'has finished the GAME'
