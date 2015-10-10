__author__ = 'vicident'

import ale_data_set

class FDataSet(ale_data_set.DataSet):

    """ Variation from DataSet:
        - image container is floatX instead of uint8
    """

    def __init__(self, width, height, rng, max_steps=1000, phi_length=4):

        ale_data_set.DataSet.__init__(self, width, height, rng, max_steps, phi_length)

        # Replace uint8 image by floatX matrix
        self.imgs = ale_data_set.np.zeros((max_steps, height, width), dtype=ale_data_set.floatX)


    def random_batch(self, batch_size):
        """Return corresponding states, actions, rewards, terminal status, and
            next_states for batch_size randomly chosen state transitions.
        """
        # Allocate the response.
        states = ale_data_set.np.zeros((batch_size,
                           self.phi_length,
                           self.height,
                           self.width),
                          dtype=ale_data_set.floatX)

        actions = ale_data_set.np.zeros((batch_size, 1), dtype='int32')
        rewards = ale_data_set.np.zeros((batch_size, 1), dtype=ale_data_set.floatX)
        terminal = ale_data_set.np.zeros((batch_size, 1), dtype='bool')
        next_states = ale_data_set.np.zeros((batch_size,
                                self.phi_length,
                                self.height,
                                self.width),
                               dtype='uint8')

        count = 0
        while count < batch_size:
            # Randomly choose a time step from the replay memory.
            index = self.rng.randint(self.bottom,
                                     self.bottom + self.size - self.phi_length)

            initial_indices = ale_data_set.np.arange(index, index + self.phi_length)
            transition_indices = initial_indices + 1
            end_index = index + self.phi_length - 1

            # Check that the initial state corresponds entirely to a
            # single episode, meaning none but the last frame may be
            # terminal. If the last frame of the initial state is
            # terminal, then the last frame of the transitioned state
            # will actually be the first frame of a new episode, which
            # the Q learner recognizes and handles correctly during
            # training by zeroing the discounted future reward estimate.
            if ale_data_set.np.any(self.terminal.take(initial_indices[0:-1], mode='wrap')):
                continue

            # Add the state transition to the response.
            states[count] = self.imgs.take(initial_indices, axis=0, mode='wrap')
            actions[count] = self.actions.take(end_index, mode='wrap')
            rewards[count] = self.rewards.take(end_index, mode='wrap')
            terminal[count] = self.terminal.take(end_index, mode='wrap')
            next_states[count] = self.imgs.take(transition_indices,
                                                axis=0,
                                                mode='wrap')
            count += 1

        return states, actions, rewards, next_states, terminal