#!/usr/bin/env python
#source ~/.bash_profile

import time
import statistics
import os
import sys
import optparse

# os.system("source ~/.bash_profile")
# we need to import some python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # Checks for the binary in environ vars
import traci

delayTime = 1/8

def reset_no_veh_waiting():
    no_veh_N = 0
    no_veh_E = 0
    no_veh_W = 0
    no_veh_S = 0

def get_options():
    opt_parser = optparse.OptionParser()
    opt_parser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = opt_parser.parse_args()
    return options


# contains TraCI control loop
def run():

    # Central Juction at gne26
    Central = "gneJ26"
    
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        # No of vehicles at NEWS intersection
        no_veh_N = 0
        no_veh_E = 0
        no_veh_W = 0
        no_veh_S = 0

        # Accumulated wait time in each direction
        wait_time_N = 0
        wait_time_E = 0
        wait_time_W = 0
        wait_time_S = 0

        traci.simulationStep()

        phase_central = traci.trafficlight.getRedYellowGreenState(Central)
        ####
        for vehicle_id in traci.vehicle.getIDList():
            vehicle_speed = traci.vehicle.getSpeed(vehicle_id)
            road_id = traci.vehicle.getRoadID(vehicle_id)
            vehicle_wait_time = traci.vehicle.getAccumulatedWaitingTime(vehicle_id)
            #print("Vehicle ID: ", vehicle_id, "Speed: ", vehicle_speed, "Road Id: ", road_id)

            #Count vehicle at the TLC junction
            if vehicle_speed < 1: # Count only stoped vehicles
                if   road_id == "eB_I": #North
                    no_veh_N += 1 
                    wait_time_N += vehicle_wait_time                    
                elif road_id == "eD_I": #East
                    no_veh_E += 1 
                    wait_time_E += vehicle_wait_time
                elif road_id == "eH_I": #West
                    no_veh_W += 1 
                    wait_time_W += vehicle_wait_time
                elif road_id == "eF_I": #South
                    no_veh_S += 1 
                    wait_time_S += vehicle_wait_time

        # Max Pressure (time based) Reducing Naive Algo
        threshold = 70
        if wait_time_N > threshold or wait_time_S >threshold:
            traci.trafficlight.setRedYellowGreenState(Central, "GGGgrrrrGGGgrrrr")
            traci.trafficlight.setPhaseDuration(Central, 5)
        elif wait_time_W > threshold or wait_time_E >threshold:
            traci.trafficlight.setRedYellowGreenState(Central, "rrrrGGGgrrrrGGGg")
            traci.trafficlight.setPhaseDuration(Central, 5)

        # Print status report
        print("--- Status Report ---")
        print("Step: ", step)
        print("Signal State: ", phase_central)

        print("no_veh_N: ", no_veh_N)
        print("no_veh_E: ", no_veh_E)
        print("no_veh_W: ", no_veh_W)
        print("no_veh_S: ", no_veh_S)

        print("wait_time_N", wait_time_N)
        print("wait_time_E", wait_time_E)
        print("wait_time_W", wait_time_W)
        print("wait_time_S", wait_time_S)

        print("Average wait time at Central Junction: ", statistics.mean((wait_time_N, wait_time_E, wait_time_W, wait_time_S)))
        print("\n")
        print("Lanes: ", traci.trafficlight.getControlledLanes(Central))
        print("Lanes: ", len(traci.trafficlight.getControlledLanes(Central)))

        ####

        tlc_list = traci.trafficlight.getIDList()

       # print("Current timestep: ", step)
        #print("TLC list: ", tlc_list)

        #traci.trafficlight.setPhase("gneJ2", 0)
        #print("gneJ2 phase: ", phase_gneJ2)
        
        #traci.trafficlight.setRedYellowGreenState("gneJ2", "GrrrrGGG")

       # det_vehs = traci.inductionloop.getLastStepVehicleIDs("det_0")
        #for veh in det_vehs:
         #   print(det_vehs)
          #  traci.vehicle.changeLane(veh, 2, 25)
 
        #if step == 100:
         #   print("Changing veh targets")
#
 #           traci.vehicle.changeTarget("1", "e9")
  #          traci.vehicle.changeTarget("3", "e9")

        time.sleep(delayTime)
        step += 1


    traci.close()
    sys.stdout.flush()


# main entry point
if __name__ == "__main__":
    options = get_options()

    # check binary
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    # traci starts sumo as a subprocess and then this script connects and runs
    traci.start([sumoBinary, "-c", "main.sumocfg",
                             "--tripinfo-output", "tripinfo.xml"])
    run()