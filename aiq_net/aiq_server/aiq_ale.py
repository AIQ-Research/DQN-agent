__author__ = 'vicident'

from aiq_net.interfaces.ile import ILearningEnvironment
from aiq_net.interfaces.iagent import IAgent
from Queue import Queue
from threading import Lock
from aiq_net.aiq_define import DEFAULT_START_REWARD
import numpy as np

# Two active threads meet here: trainer thread and market listener thread
class TGEInterface(ILearningEnvironment, IAgent):

    def __init__(self):
        # Thread-safe queues work as buffers with retrieval
        self.reward_queue = Queue(1)
        self.actions_queue = Queue(1)

        # Two threads may have an access to these variables simultaneously
        self.terminal = False
        self.observation = None

        # Mutex for 'terminal' and 'observation'
        self.lock = Lock()

    def load_tge_from_json(self, json):
        pass

    def act(self, action):
        # free 'start_episode' and 'step' methods
        self.actions_queue.put(action)

        return self.reward_queue.get()

    def game_over(self):
        self.lock.acquire()
        terminal = self.terminal
        self.lock.release()

        return terminal

    def reset_game(self):
        # we can't control the market
        pass

    def getMinimalActionSet(self): pass

    def getScreenDims(self): pass

    def lives(self): pass

    def getScreenGrayscale(self, screen_buffer):
        self.lock.acquire()
        # copy actual frame to buffer
        np.copyto(screen_buffer, self.observation)
        self.lock.release()

    def start_episode(self, observation):
        self.lock.acquire()
        self.observation = observation
        self.lock.release()
        self.reward_queue.put(DEFAULT_START_REWARD)

        return self.actions_queue.get()

    def step(self, reward, observation):
        self.lock.acquire()
        self.observation = observation
        self.lock.release()
        self.reward_queue.put(reward)

        return self.actions_queue.get()

    def end_episode(self, reward, terminal=True):
        self.lock.acquire()
        self.terminal = terminal
        self.lock.release()

        # free 'act' method
        self.reward_queue.put(reward)
