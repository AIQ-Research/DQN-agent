__author__ = 'vicident'

from q_network import DeepQLearner

# Delegation of DeepQLearner:
# https://en.wikipedia.org/wiki/Delegation_(programming)
class AIQLearner:

    # Delegated methods

    def __init__(self, input_width, input_height, num_actions,
                 num_frames, discount, learning_rate, rho,
                 rms_epsilon, momentum, clip_delta, freeze_interval,
                 batch_size, network_type, update_rule,
                 batch_accumulator, rng, input_scale=255.0):

        self.deep_q_learner = DeepQLearner(input_width, input_height, num_actions,
                 num_frames, discount, learning_rate, rho,
                 rms_epsilon, momentum, clip_delta, freeze_interval,
                 batch_size, network_type, update_rule,
                 batch_accumulator, rng, input_scale)

        self.num_frames = self.deep_q_learner.num_frames
        self.input_width = self.deep_q_learner.input_width
        self.input_height = self.deep_q_learner.input_height
        self.lr = self.deep_q_learner.lr
        self.discount = self.deep_q_learner.discount
        self.num_actions = self.deep_q_learner.num_actions
        self.batch_size = self.deep_q_learner.batch_size

    def build_network(self, network_type, input_width, input_height,
                      output_dim, num_frames, batch_size):

        if network_type == "linear":
            return self.build_linear_network(input_width, input_height,
                                             output_dim, num_frames, batch_size)
        else:
            raise ValueError("Unrecognized network: {}".format(network_type))

    def train(self, states, actions, rewards, next_states, terminals):
        return self.deep_q_learner.train(states, actions, rewards, next_states, terminals)

    def q_vals(self, state):

        return self.deep_q_learner.q_vals(state)

    def choose_action(self, state, epsilon):

        return self.deep_q_learner.choose_action(state, epsilon)

    def reset_q_hat(self):

        self.deep_q_learner.reset_q_hat()

    def build_linear_network(self, input_width, input_height, output_dim,
                             num_frames, batch_size):

        self.deep_q_learner.build_linear_network(input_width, input_height, output_dim,
                             num_frames, batch_size)

    # New methods

    def build_1H_layer_network(self, input_width, input_height, output_dim,
                             num_frames, batch_size):
        raise("Hasn't been ready yet")
