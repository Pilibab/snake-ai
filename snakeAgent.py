import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import random
import config
from model import DQN


class Agent:
    def __init__(self, state_size = 5, ouput_size = 3):
        self.state_size = state_size
        self.action_size = ouput_size
        # Constants / hyper parameters
        self.alpha = config.AlPHA
        self.epsilon = config.EPSILON
        self.eps_decy = config.EPS_DECAY
        self.eps_min = config.EPS_MIN
        self.gamma = config.GAMMA

        self.memory = deque(maxlen=config.MEMORY)
        self.batch_size = config.BATCH_SIZE

        self.reward = {
            "eat": 10,
            "death": -100,
            "move_close": .01,
            "time_score_decay": -0.05,
        }
        # Neural network 
        self.model = DQN(state_size, 256, ouput_size)
        self.optimizer = optim.Adam(self.model.parameters(), lr = self.alpha)
        self.criterion = nn.MSELoss()

    def get_action(self, state):
        final_state = state

        state = torch.tensor(final_state, dtype=torch.float).unsqueeze(0)

        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)
        else: 
            with torch.no_grad():
                q_val = self.model(state)               # Returns the output layer, size=3 (e.g. [0.3,0.67, 0.9])
                return torch.argmax(q_val).item()       

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action ,reward, next_state, done))


    def learn_long_term(self):
        if len(self.memory) < self.batch_size:
            return 
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.tensor(states, dtype=torch.float)       
        actions = torch.tensor(actions)
        rewards = torch.tensor(rewards, dtype=torch.float)
        next_states = torch.tensor(next_states, dtype=torch.float)
        dones = torch.tensor(dones, dtype=torch.bool)

        q_val = self.model(states)
        targets = q_val.clone() # -> what is this for?

        # dont get everything under this
        for i in range(self.batch_size):
            q_update = rewards[i]
            if not dones[i]:
                q_update = rewards[i] + self.gamma * torch.max(self.model(next_states[i]))
            targets[i][torch.argmax(actions[i])] = q_update

        self.optimizer.zero_grad()
        loss = self.criterion(q_val, targets)

        loss.backward()
        self.optimizer.step()

    def learn_short_term(self, state, action ,reward, next_state, done):
        if len(self.memory) < self.batch_size:
            return 
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)

        state = torch.unsqueeze(state, 0)
        next_state = torch.unsqueeze(next_state, 0)
        action = torch.unsqueeze(action, 0)
        reward = torch.unsqueeze(reward, 0)

        q_val = self.model(state)
        target = q_val.clone()

        if not done:
            q_update = reward + self.gamma * torch.max(self.model(next_state))
        else:
            q_update = reward
        
        target[0][action] = q_update

        self.optimizer.zero_grad()
        loss = self.criterion(q_val, target)

        loss.backward()
        self.optimizer.step()
        
    def decay_exploration(self):
        if self.epsilon > self.eps_min:
            self.epsilon *= self.eps_decy
