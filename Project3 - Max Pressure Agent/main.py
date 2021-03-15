from sumo1 import SimEnv
import time
import traci
from MaxPressureAgent import MaxPressureAgent
import numpy as np
import matplotlib.pyplot as plt



def save_plot(list):
    x = [i for i in range(len(list))]
    N = len(list)
    running_avg = np.empty(N)
    for t in range(N):
        running_avg[t] = np.mean(scores[max(0, t-100):(t+1)])

    plt.plot(x, running_avg)
    plt.savefig("reward plot.png") # save as png

if __name__ == '__main__':
    env = SimEnv()
    env.start_sumo()
        
    step = 0
    delayTime = 1/8

    Central = "gneJ26"
    scores=[]

    agent_0 = MaxPressureAgent(Central, 70)
    # also look into dynamic action as per number of lanes
    score = 0

    agnetBusy = False

    # Agent busy issue
    while step <500:#traci.simulation.getMinExpectedNumber() > 0:

        if step == 0:
            action = "GGGgrrrrGGGgrrrr" # A random action in the beginning
        else:
            obs_, reward, info = agent_0.step(action, step)
            print("obs_", obs_)

            score += reward

            action = agent_0.choose_action(obs_)
        
            scores.append(score)
            avg_score = np.mean(scores[-100:])

            agent_0.printStatusReport(step)
            print("State: ", obs_)
            print("REWARD: ", reward)
            print("Acct wait time: ", agent_0.acc_wait_time)
            print("Score: ", score)
            


        time.sleep(delayTime)

        # new env class
#        traci.trafficlight.setRedYellowGreenState(agent_0.TLC_name, action)
 #       traci.trafficlight.setPhaseDuration(agent_0.TLC_name, 5)


        env.simulationStep()
        step+=1

    save_plot(scores)
    env.close_sumo() 



        
 