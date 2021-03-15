import traci
import random
import statistics as stat

import numpy as np
import torch as T
from neural_network import LinearDeepQNetwork
 
class DQAgent(object):
    """
        This is single agent class.
    """
    def __init__(self, TLC_name, input_dims=8, n_actions=2, lr, gamma=0.99,\
                    epsolon = 1.0, eps_dec=1e05, eps_min=0.01):
        # Agent defailt parameters
        self.lr = lr
        self.input_dims = input_dims
        self.n_actions = n_actions
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_dec = eps_dec
        self.eps_min = eps_min

        self.action_space = [i for i in range(self.n_actions)]

        #Init Q learning network
        self.Q = LinearDeepQNetwork(self.lr, self.n_actions, self.input_dims)

        ## Defining cardinal parameters
        # Accumulated traffic queues in each direction
        self.no_veh_N = 0
        self.no_veh_E = 0
        self.no_veh_W = 0
        self.no_veh_S = 0

        # Accumulated wait time in each direction
        self.wait_time_N = 0
        self.wait_time_E = 0
        self.wait_time_W = 0
        self.wait_time_S = 0

        self.TLC_name = TLC_name
        self.threshold = threshold

        self.acc_wait_time = []

        self.reward = 0

        self.switch_time = 0
        self.next_switch = 0
        
    def get_reward(self):

        current_wait_time = self.get_avg_wait_time()
        if len(self.acc_wait_time) == 0:
            self.reward = 0
        else:
            self.reward = self.acc_wait_time[-1] - current_wait_time
        
        self.acc_wait_time.append(current_wait_time)

        if len(self.acc_wait_time) > 3: # to reduce the array size  / keep only last three elements
            self.acc_wait_time = self.acc_wait_time[-3:]

        return self.reward

    def get_avg_wait_time(self):
        phase_central = traci.trafficlight.getRedYellowGreenState(self.TLC_name)
            ####
        for vehicle_id in traci.vehicle.getIDList():
            vehicle_speed = traci.vehicle.getSpeed(vehicle_id)
            road_id = traci.vehicle.getRoadID(vehicle_id)
            vehicle_wait_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            #print("Vehicle ID: ", vehicle_id, "Speed: ", vehicle_speed, "Road Id: ", road_id)

            #Count vehicle at the TLC junction
            if vehicle_speed < 1: # Count only stoped vehicles
                if   road_id == "eB_I": #North
                    self.no_veh_N += 1 
                    self.wait_time_N += vehicle_wait_time                    
                elif road_id == "eD_I": #East
                    self.no_veh_E += 1 
                    self.wait_time_E += vehicle_wait_time
                elif road_id == "eH_I": #West
                    self.no_veh_W += 1 
                    self.wait_time_W += vehicle_wait_time
                elif road_id == "eF_I": #South
                    self.no_veh_S += 1 
                    self.wait_time_S += vehicle_wait_time

        return stat.mean([self.wait_time_N, self.wait_time_E, self.wait_time_W, self.wait_time_S])

    def step(self, action, step):

        # 1st APPLY the choosed action
        if action == "0":
            traci.trafficlight.setRedYellowGreenState(self.TLC_name, "GGGgrrrrGGGgrrrr")
        elif action == "1":
            traci.trafficlight.setRedYellowGreenState(self.TLC_name, "rrrrGGGgrrrrGGGg")

        # 2nd, find the Reward 
        #func will be implemented later
        reward = self.get_reward()
        
        # 3rd: find new state
        # return state, reward, info_dict
        state = self.get_state()
        
        #state = [self.wait_time_N, self.wait_time_E, self.wait_time_W, self.wait_time_S,
         #        self.no_veh_N, self.no_veh_E, self.no_veh_W, self.no_veh_S]
        
        # 4th, an info dict
        info = {"TLC_name": self.TLC_name}

        return state, reward, info


        #zero all the class variable

    def get_state(self):
        phase_central = traci.trafficlight.getRedYellowGreenState(self.TLC_name)
        ####
        for vehicle_id in traci.vehicle.getIDList():
            vehicle_speed = traci.vehicle.getSpeed(vehicle_id)
            road_id = traci.vehicle.getRoadID(vehicle_id)
            vehicle_wait_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            #print("Vehicle ID: ", vehicle_id, "Speed: ", vehicle_speed, "Road Id: ", road_id)

            #Count vehicle at the TLC junction
            if vehicle_speed < 1: # Count only stoped vehicles
                if   road_id == "eB_I": #North
                    self.no_veh_N += 1 
                    self.wait_time_N += vehicle_wait_time                    
                elif road_id == "eD_I": #East
                    self.no_veh_E += 1 
                    self.wait_time_E += vehicle_wait_time
                elif road_id == "eH_I": #West
                    self.no_veh_W += 1 
                    self.wait_time_W += vehicle_wait_time
                elif road_id == "eF_I": #South
                    self.no_veh_S += 1 
                    self.wait_time_S += vehicle_wait_time

        state_space = [self.wait_time_N, self.wait_time_E, self.wait_time_W, self.wait_time_S,
                 self.no_veh_N, self.no_veh_E, self.no_veh_W, self.no_veh_S]
        
        return np.array(state_space)

    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            state = T.tensor(observation, dtype=T.float).to(self.Q.device)
            actions = self.Q.forward(state)
            action = T.argmax(actions).item()
        else:
            action = np.random.choice(self.action_space)
        
        self.reset_lane_traffic_info_params()

        return action
        
    def reset_lane_traffic_info_params(self):
        # Accumulated traffic queues in each direction
        self.no_veh_N = 0
        self.no_veh_E = 0
        self.no_veh_W = 0
        self.no_veh_S = 0

        # Accumulated wait time in each direction
        self.wait_time_N = 0
        self.wait_time_E = 0
        self.wait_time_W = 0
        self.wait_time_S = 0

    def decrement_epsilon(self):
        self.epsilon = self.epsilon - self.eps_dec \
                        if self.epsilon > self.eps_min else self.eps_min
                        
    def learn(self, state, action, reward, state_):
        self.Q.optimizer.zero_grad()
        states = T.tensor(state, dtype = T.float).to(self.Q.device)
        actions = T.tensor(action).to(self.Q.device)
        rewards = T.tensor(reward).to(self.Q.device)
        states_ = T.tensor(state_, dtype=T.float).to(self.Q.device)


        q_pred = self.Q.forward(states)[actions]

        q_next = self.Q.forward(states_).max()

        q_target = rewards + self.gamma * q_next

        loss = self.Q.loss(q_target, q_pred).to(self.Q.device)

        loss.backward()

        self.Q.optimizer.step()
        self.decrement_epsilon()
        
    def printStatusReport(self, step):
        # Print status report
        phase_central = traci.trafficlight.getRedYellowGreenState(self.TLC_name)

        print("--- Status Report ---")
        print("Step: ", step)
        print("Signal State: ", phase_central)
        print("Last switch time at action: ", self.switch_time)
        print("Get next switch: ", (-self.switch_time + traci.trafficlight.getNextSwitch(self.TLC_name)))
        print("Get phase duration: ", (-self.switch_time + traci.trafficlight.getPhaseDuration(self.TLC_name)))


        print("no_veh_N: ", self.no_veh_N)
        print("no_veh_E: ", self.no_veh_E)
        print("no_veh_W: ", self.no_veh_W)
        print("no_veh_S: ", self.no_veh_S)

        print("wait_time_N", self.wait_time_N)
        print("wait_time_E", self.wait_time_E)
        print("wait_time_W", self.wait_time_W)
        print("wait_time_S", self.wait_time_S)

