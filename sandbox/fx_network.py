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

def fx_cnn_v0(agent, env, dropout=0, learning_rate=1e-3, **args):
    S = Input(shape=[agent.input_dim])
    #h = Reshape( agent.input_dim_orig )(S)
    h = S
    h = TimeDistributed( Convolution1D(16, 60, subsample_length=4, border_mode='same', activation='relu'))(h)
    h = TimeDistributed( Convolution1D(32, 30, subsample_length=4, border_mode='same', activation='relu'))(h)
    h = Flatten()(h)
    h = Dense(256, activation='relu')(h)
    V = Dense(env.action_space.n, activation='linear',init='zero')(h)
    model = Model(S, V)
    model.compile(loss='mse', optimizer=RMSprop(lr=learning_rate) )
    return model

def fx_cnn_v1(agent, env, dropout=0.5, **args):
    S = Input(shape=[agent.input_dim])
    h = Dense(1440, activation='relu', init='he_normal')(S)
    h = Dropout(dropout)(h)
    h = Dense(1440, activation='relu', init='he_normal')(h)
    h = Dropout(dropout)(h)
    V = Dense(env.action_space.n, activation='linear',init='zero')(h)
    model = Model(S,V)
    model.compile(loss='mse', optimizer=RMSprop(lr=args["learning_rate"]) )
    return model