__author__ = 'vicident'

from abc import ABCMeta, abstractmethod

class ILearningEnvironment:
    __metaclass__ = ABCMeta

    @abstractmethod
    def act(self, action): pass

    @abstractmethod
    def game_over(self): pass

    @abstractmethod
    def reset_game(self): pass

    @abstractmethod
    def getMinimalActionSet(self): pass

    @abstractmethod
    def getScreenDims(self): pass

    @abstractmethod
    def getScreenGrayscale(self, screen_buffer): pass

    @abstractmethod
    def lives(self): pass