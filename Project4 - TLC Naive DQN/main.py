from includes.sumo import SimEnv

import time
import traci
import numpy as np
import matplotlib.pyplot as plt

from includes.DQAgent import DQAgent
from includes.utils import plot_learning_curve

if __name__ == '__main__':
    env = SimEnv()
    env.start_sumo()
        
    step = 0
    delayTime = 0#1/8

    Central = "gneJ26"
    n_games = 100000
    scores = []
    eps_history = []

    agent = DQAgent(TLC_name = Central, lr=0.0001, input_dims=8, \
                    n_actions = 2)

    action = 0 #random action
    obs, reward, info = agent.step(action, step)

    for i in range(n_games):
        score = 0
        action = agent.choose_action(obs)
        obs_, reward, info = agent.step(action, step)
        score += reward
        agent.learn(obs, action, reward, obs_)
        obs = obs_
        
        scores.append(score)
        eps_history.append(agent.epsilon)

        if i % 100 == 0:
            avg_score = np.mean(scores[-100:])
            print('episode ', i, 'score %.1f avg score %.1f epsilon %.2f' %
                  (score, avg_score, agent.epsilon))
        
        time.sleep(delayTime)
        env.simulationStep()
        step+=1


    filename = 'TLC_naive_dqn.png'
    x = [i+1 for i in range(n_games)]
    plot_learning_curve(x, scores, eps_history, filename)

    env.close_sumo() 