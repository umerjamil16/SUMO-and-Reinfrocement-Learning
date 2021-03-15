import traci
import random
import statistics as stat
 
class MaxPressureAgent(object):
    """
        This is single agent class.
    """
    def __init__(self, TLC_name, threshold):
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

        if len(self.acc_wait_time) > 3: # to reduce the aray size  / keep only last three elements
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

        return stat.mean([self.wait_time_N+ self.wait_time_E+ self.wait_time_W+ self.wait_time_S])

    def step(self, action, step):
        # First APPLY the choosed action
        if action != "Nil":
            traci.trafficlight.setRedYellowGreenState(self.TLC_name, action)
            traci.trafficlight.setPhaseDuration(self.TLC_name, 5)
            self.switch_time = step

        #simStep

        # 2nd, find the Reward 
        #func will be implemented later
        reward = self.get_reward()
        
        # 3rd: find new state
        # return state, reward, info_dict
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

        state = [self.wait_time_N, self.wait_time_E, self.wait_time_W, self.wait_time_S]
        #state = [self.wait_time_N, self.wait_time_E, self.wait_time_W, self.wait_time_S,
         #        self.no_veh_N, self.no_veh_E, self.no_veh_W, self.no_veh_S]
        
        # 4th, an info dict
        info = {"TLC_name": self.TLC_name}

        return state, reward, info


        #zero all the class variable


    def choose_action(self, state):
        # if else conditioning on state space based
        # feedforward part
        if state[0] > self.threshold or state[3] > self.threshold:
            action = "GGGgrrrrGGGgrrrr"
        elif state[1] > self.threshold or state[2] > self.threshold:
            action = "rrrrGGGgrrrrGGGg"
        else: #random action, #need to be fixed later
            action = "Nil"


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

        return action






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

