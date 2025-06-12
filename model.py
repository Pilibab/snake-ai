import torch
import torch.nn as nn
import torch.nn.functional as F
import os

class DQN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(DQN, self).__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        return self.linear2(x)
    
    def save_model(self, file_name, episode):
        print("\n\nMODEL SAVED!!!\n\n")
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file = f"{file_name}_ep_{episode}.pth"
        torch.save(self.state_dict(), file)

    def load_model(self, FILE_PATH):
        self.model.load_state_dict(torch.load(FILE_PATH))
        self.model.eval()