__author__ = 'vicident'

from ale_agent import NeuralAgent
from aiq_net.interfaces.iagent import IAgent
import aiq_data_set

# Inherit basic abstract methods from IAgent and their realizations from ale_agent.NeuralAgent
class AIQAgent(NeuralAgent, IAgent):

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
