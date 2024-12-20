import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import os

class Linear_QNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.Linear1 = nn.Linear(input_size, hidden_size)
        self.Linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.Linear1(x))
        x = self.Linear2(x)
        #x = self.Linear3(x)
        return x
    
    def save(self, file_name = 'model.pth'):
        model_folder_path = './model'
        if not os.path.exists(model_folder_path):
            os.makedirs(model_folder_path)
        file_name = os.path.join(model_folder_path, file_name)
        torch.save(self.state_dict(), file_name)

class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr = self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)
        #(n, x)

        if len(state.shape) == 1:
            #(1, x)
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )

        #1 - predicted Qvalues with current state
        prediction = self.model(state)

        target = prediction.clone()
        for idx in range(len(done)):
            Qnew = reward[idx]
            if not done[idx]:
                Qnew = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Qnew

        #2 - Qnew = r + gamma * max(next_predicted Qvalue) -> only do this if not done
        #prediction.clone()
        #predictions[argmax(action)] = Qnew
        self.optimizer.zero_grad()
        loss = self.criterion(target, prediction)
        loss.backward()

        self.optimizer.step()