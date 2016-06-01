__author__ = 'vicident'

from aiq_net import aiq_network
from aiq_net.aiq_db import connectors
from aiq_net.aiq_ale.aiq_ale import FxLocalALE
from aiq_network import AIQLearner
from aiq_agent import AIQAgent
import cv2

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

def test_aiq_db(db_path):
    db = connectors.SqliteConnector()
    db.connect(db_path)
    table_names = db.get_tables()
    columns = db.get_table_columns(table_names[0])
    print columns
    db.close()


def test_aiq_ale(db_path):
    rng = np.random.RandomState(1234567)
    ale = FxLocalALE(db_path, 64, [1, 5, 15, 30, 60, 120], rng)
    ale._time_pointer += 8 * 60
    h, w = ale.getScreenDims()
    print "w:", w, "h:", h
    screen_buffer = np.zeros((h, w), dtype=floatX)
    ale.reset_game()
    ale.getScreenGrayscale(screen_buffer)
    img = np.asarray(screen_buffer*255, dtype=np.ubyte)
    # debug
    cv2.imwrite("data_frame.png", img)
    print img

if __name__ == '__main__':
    #test_aiq_agent()
    test_aiq_ale('/home/vicident/Development/data/fxpairs2008.db')
