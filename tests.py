__author__ = 'vicident'

from aiq_net import aiq_network
from aiq_net.aiq_db import connectors
from aiq_net.aiq_ale.aiq_ale import FxLocalALE
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

def test_aiq_db(db_path):
    db = connectors.SqliteConnector()
    db.connect(db_path)
    table_names = db.get_tables()
    columns = db.get_table_columns(table_names[0])
    print columns
    #table = db.read_table(table_names[0])
    #sub_table = db.read_table_range(table_names[0], columns, 'time', 1389946680000, 1389948120000)
    #print sub_table
    db.close()

def test_aiq_ale(db_path):
    ale = FxLocalALE(db_path)
    print ale

if __name__ == '__main__':
    #test_aiq_agent()
    test_aiq_ale('/home/vicident/Development/AIQ/db/fxpairs.db')
