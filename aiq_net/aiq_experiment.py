__author__ = 'vicident'

import numpy as np
from ale_experiment import ALEExperiment
from ale_data_set import floatX

class AIQExperiment(ALEExperiment):
    def __init__(self, ale, agent, resized_width, resized_height,
                 resize_method, num_epochs, epoch_length, test_length,
                 frame_skip, death_ends_episode, max_start_nullops, rng):

        ALEExperiment.__init__(self, ale, agent, resized_width, resized_height,
                 resize_method, num_epochs, epoch_length, test_length,
                 frame_skip, death_ends_episode, max_start_nullops, rng)

        # change self.buffer_length and init screen_buffer

        self.screen_buffer = np.empty((self.buffer_length,
                                       self.height, self.width),
                                      dtype=floatX)


    def get_observation(self):

        assert self.buffer_count >= 2
        index = self.buffer_count % self.buffer_length - 1

        return self.screen_buffer[index, ...]
