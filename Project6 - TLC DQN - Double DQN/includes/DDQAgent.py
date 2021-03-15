import traci
import random
import statistics as stat

import numpy as np
import torch as T
from includes.deep_q_network import DeepQNetwork
from includes.replay_memory import ReplayBuffer

class DDQAgent(object):
    """
        This is single agent class.
    """
    def __init__(self, gamma, epsilon, lr, n_actions, input_dims,
                 mem_size, batch_size, eps_min=0.01, eps_dec=5e-7,
                 replace=1000, algo=None, env_name=None, chkpt_dir='tmp/dqn', TLC_name="gneJ26"):
        self.gamma = gamma
        self.epsilon = epsilon
        self.lr = lr
        self.n_actions = n_actions
        self.input_dims = input_dims
        self.batch_size = batch_size
        self.eps_min = eps_min
        self.eps_dec = eps_dec
        self.replace_target_cnt = replace
        self.algo = algo
        self.env_name = env_name
        self.chkpt_dir = chkpt_dir
        self.action_space = [i for i in range(n_actions)]
        self.learn_step_counter = 0

        self.memory = ReplayBuffer(mem_size, input_dims, n_actions)

        self.q_eval = DeepQNetwork(self.lr, self.n_actions,
                                    input_dims=self.input_dims,
                                    name=self.env_name+'_'+self.algo+'_q_eval',
                                    chkpt_dir=self.chkpt_dir)

        self.q_next = DeepQNetwork(self.lr, self.n_actions,
                                    input_dims=self.input_dims,
                                    name=self.env_name+'_'+self.algo+'_q_next',
                                    chkpt_dir=self.chkpt_dir)


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
        self.threshold = 0

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
            state = T.tensor(observation,dtype=T.float).to(self.q_eval.device)
            actions = self.q_eval.forward(state)
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
                        

    def store_transition(self, state, action, reward, state_):
        self.memory.store_transition(state, action, reward, state_)

    def sample_memory(self):
        state, action, reward, new_state = \
                                self.memory.sample_buffer(self.batch_size)

        states = T.tensor(state).to(self.q_eval.device)
        rewards = T.tensor(reward).to(self.q_eval.device)
        actions = T.tensor(action).to(self.q_eval.device)
        states_ = T.tensor(new_state).to(self.q_eval.device)

        return states, actions, rewards, states_

    def replace_target_network(self):
        if self.learn_step_counter % self.replace_target_cnt == 0:
            self.q_next.load_state_dict(self.q_eval.state_dict())

    def decrement_epsilon(self):
        self.epsilon = self.epsilon - self.eps_dec \
                           if self.epsilon > self.eps_min else self.eps_min

    def save_models(self):
        self.q_eval.save_checkpoint()
        self.q_next.save_checkpoint()

    def load_models(self):
        self.q_eval.load_checkpoint()
        self.q_next.load_checkpoint()

    def learn(self):
        if self.memory.mem_cntr < self.batch_size:
            return

        self.q_eval.optimizer.zero_grad()

        self.replace_target_network()

        states, actions, rewards, states_ = self.sample_memory()
        indices = np.arange(self.batch_size)

        q_pred = self.q_eval.forward(states)[indices, actions]
        q_next = self.q_next.forward(states_)
        q_eval = self.q_eval.forward(states_)

        max_actions = T.argmax(q_eval, dim=1)


        q_target = rewards + self.gamma*q_next[indices, max_actions]

        loss = self.q_eval.loss(q_target, q_pred).to(self.q_eval.device)
        loss.backward()

        self.q_eval.optimizer.step()
        self.learn_step_counter += 1

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

