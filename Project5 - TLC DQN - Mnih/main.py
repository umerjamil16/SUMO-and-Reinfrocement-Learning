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
    n_games = 5000
    n_steps = 0

    scores = []
    eps_history = []
    steps_array = []

    best_score = -np.inf
    load_checkpoint = False

    agent = DQAgent(gamma=0.99, epsilon=1, lr=0.0001,
                     input_dims=8,
                     n_actions=2, mem_size=50000, eps_min=0.1,
                     batch_size=32, replace=1000, eps_dec=1e-5,
                     chkpt_dir='models/', algo='DQNAgent',
                     env_name='SUMO_tlc', TLC_name = Central)

    if load_checkpoint:
        agent.load_models()

    observation, reward, info = agent.step(0, step) #taking random action

    for i in range(n_games):
        score = 0
        action = agent.choose_action(observation)
        observation_, reward, info = agent.step(action, step)
        score += reward
    
        if not load_checkpoint:
            agent.store_transition(observation, action, reward, observation_)
            agent.learn()
                
        observation = observation_
        n_steps += 1
        
        scores.append(score)
        steps_array.append(n_steps)
        

        avg_score = np.mean(scores[-100:])
        print('episode: ', i,'score: ', score,
             ' average score %.1f' % avg_score, 'best score %.2f' % best_score,
            'epsilon %.2f' % agent.epsilon, 'steps', n_steps)

        if avg_score > best_score:
            if not load_checkpoint:
                agent.save_models()
            best_score = avg_score

        eps_history.append(agent.epsilon)

        time.sleep(delayTime)
        env.simulationStep()
        step+=1

    x = [i+1 for i in range(len(scores))]
    filename = 'TLC_naive_dqn.png'
    plot_learning_curve(steps_array, scores, eps_history, filename)

    env.close_sumo() 