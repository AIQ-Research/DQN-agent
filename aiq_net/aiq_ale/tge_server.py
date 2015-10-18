__author__ = 'vicident'

import socket
import struct
import array
import numpy

class TraderGameEnvironment:

    HOST = "localhost"
    PORT = 6666
    BACKLOG = 5

    # trader.dukascopy.sandbox.GameState
    CONTINUE_PLAY = 0
    NEXT_GAME = 1
    LOSE_GAME = -1

    @staticmethod
    def recvall(sock, n):
        data = ''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def __init__(self, host, port, callback):
        self.callback = callback # ITraderAgent
        self.servsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.servsock.bind((host, port))
        self.servsock.listen(self.BACKLOG)
        self.initial_deposit = 5000 # initial deposit --> TODO: should be loaded from conf
        self.prev_reward = 0

    def play(self):
        # infinite loop
        while True:
            # wait for new connection
            clisock, address = self.servsock.accept()

            # receive game state
            bytes = TraderGameEnvironment.recvall(clisock, 4)
            game_state = struct.unpack("i", bytes)[0]

            # receive and unpack
            bytes = TraderGameEnvironment.recvall(clisock, 4)
            rows = struct.unpack("i", bytes)[0]
            bytes = TraderGameEnvironment.recvall(clisock, 4)
            cols = struct.unpack("i", bytes)[0]

            # receive and unpack currency frame
            bytes = TraderGameEnvironment.recvall(clisock, rows*cols*8)
            frameLine = struct.unpack("d"*rows*cols, bytes)
            frameList = array.array("d", frameLine)
            frameList = frameList.tolist()

            # check received data
            if len(frameList) != rows*cols:
                raise "BAD: data matrix corruption!"

            # convert list to numpy array
            dataMatrix = numpy.asarray(frameList)
            dataMatrix = numpy.reshape(dataMatrix, (rows, cols))

            reward = (dataMatrix[rows-1, cols-1] - self.initial_deposit) - self.prev_reward
            action = 0

            ##### PLAY GAME

            if(game_state == self.LOSE_GAME):
                self.callback.end_episode(reward, True)
            elif(game_state == self.NEXT_GAME):
                self.callback.end_episode(reward, False)
                action = self.callback.start_episode(dataMatrix)
            elif(game_state == self.CONTINUE_PLAY):
                action = self.callback.step(reward, dataMatrix)

            #####

            self.prev_reward = dataMatrix[rows-1, cols-1] - self.initial_deposit

            clisock.send(array.array('i', [action]).tostring())
            clisock.close()

    def destroy(self):
        self.servsock.close()