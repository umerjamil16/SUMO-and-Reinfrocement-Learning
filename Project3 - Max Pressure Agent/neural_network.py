import torch.nn as nn
import torch.nn.functional as F
import torch .optim as optim
import torch as T 

class LinearDeepQNetwork(nn.Module):
    def __init__(self, lr, n_actions, input_dims):
        super(LinearDeepQNetwork, self).__init__()
#        print("*input_dims: ", input_dims)

        self.fc1 = nn.Linear(input_dims, 64) #* keyword is used for unpacking list
        self.fc2 = nn.Linear(64, n_actions)

        self.optimizer = optim.Adam(self.parameters(), lr = lr)

        self.loss = nn.MSELoss()

        self.device = T.device('cuda:0' if T.cuda.is_available() else 'cpu')

        self.to(self.device)

    def forward(self, state):
        layer1 = F.relu(self.fc1(state))
        actions = self.fc2(layer1)

        return actions

    