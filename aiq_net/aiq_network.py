import sys
# add deep_q_rl to the python search path
sys.path.append('../deep_q_rl/deep_q_rl/')

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

def main():
    net = AIQLearner(84, 84, 16, 4, .99, 0.95, .00025, .95, .95, 0.1, 10000, 32, 'linear', 'deepmind_rmsprop', 'sum', 12345)

if __name__ == '__main__':
    main()
