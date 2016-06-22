__author__ = 'vicident'

import keras.backend as K
import numpy as np
from keras.layers.embeddings import Embedding
from keras.layers.convolutional import Convolution1D, MaxPooling1D
from keras.layers.core import Dense, Dropout, Activation, Flatten, Reshape
from keras.layers.recurrent import LSTM
from keras.layers.embeddings import Embedding
from keras.models import Model
from keras.layers import Convolution2D, Dense, Flatten, Input, merge, Lambda, TimeDistributed
from keras.optimizers import RMSprop, Adadelta, Adam
import tensorflow as tf

K.set_learning_phase(True)

def fx_dnn_v0(agent, env, dropout=0.5, **args):
  with tf.device("/cpu:0"):
    state = tf.placeholder('float', [None, agent.input_dim])
    S = Input(shape=[agent.input_dim])
    h = Dense(1440, activation='relu', init='he_normal')(S)
    h = Dropout(dropout)(h)
    h = Dense(1440, activation='relu', init='he_normal')(h)
    h = Dropout(dropout)(h)
    V = Dense(env.action_space.n, activation='linear',init='zero')(h)
    model = Model(S,V)
    return state, model

def fx_rnn_v0(agent, env, dropout=0.5, h0_width=64, h1_width=8, **args):
  with tf.device("/cpu:0"):
    state = tf.placeholder('float', [None, agent.input_dim])
    S = Input(shape=[agent.input_dim])
    h = Reshape([agent.nframes, agent.input_dim/agent.nframes])(S)
    h = TimeDistributed(Dense(h0_width, activation='relu', init='he_normal'))(h)
    h = Dropout(dropout)(h)
    h = LSTM(h1_width, return_sequences=True)(h)
    h = Dropout(dropout)(h)
    h = LSTM(h1_width)(h)
    h = Dropout(dropout)(h)
    V = Dense(env.action_space.n, activation='linear',init='zero')(h)
    model = Model(S,V)
    return state, model
