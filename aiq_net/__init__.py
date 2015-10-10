__author__ = 'vicident'

import sys, os

# Set python environment

from aiq_define import DEEP_Q_RL_REL_PATH
DEEP_Q_RL_PATH = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + DEEP_Q_RL_REL_PATH)

# add deep_q_rl to the python search path
if DEEP_Q_RL_PATH not in sys.path:
    sys.path.append(DEEP_Q_RL_PATH)

AIQ_PATH = os.path.dirname(os.path.abspath(__file__))

# add aiq_net to the python search path
if AIQ_PATH not in sys.path:
    sys.path.append(AIQ_PATH)