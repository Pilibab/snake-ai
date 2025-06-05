import config
import pygame
from snake import Snake
from random import random, randint
from collections import deque

class Agent:
    def __init__(self):
        self.alpha = config.AlPHA
        self. epsilon = 1.0
        self.eps_decy = .999
        self.eps_min = 0.1

        self.memory = deque(maxlen=1000)

        self.action = [
            [1,0,0],        # turn left
            [0,1,0],        # turn forward
            [0,0,1]         # turn right 
        ]
        
        self.reward = {
            "eat": 10,
            "death": -100,
            "time_score_decay": -.1,
        }

        self.Q_table = {}  # TODO: add a 1k len buffer

    def get_action(self, state):
        state = tuple(state[:-1])

        if state not in self.Q_table:
            self.Q_table[state] = [0, 0, 0]

        if random() < self.epsilon:
            act_index = randint(0,2)
        else: 
            # from q table return the index with the highest probability among action 
            # NOTE: that q_table -> (state) -> tuple : [self.action[nth]]
            act_index = self.Q_table[state].index(max(self.Q_table[state]))
        
        return self.action[act_index], act_index
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action ,reward, next_state, done))

    def save_model(self, FILE_PATH):
        pass

    def load_model(self, FILE_PATH):
        pass

    def learn(self):
        pass

    def decay_exploartion(self):
        if self.epsilon > self.eps_min:
            self.epsilon *= self.eps_decy
