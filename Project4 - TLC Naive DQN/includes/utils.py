import matplotlib.pyplot as plt
import numpy as np

def plot_learning_curve(x, scores, epsilons, filename):
    print("in here")
    fig = plt.figure()
    ax = fig.add_subplot(111, label="1")
    ax2 = fig.add_subplot(111, label="2", frame_on=False)

    ax.plot(x, epsilons, color="blue")
    ax.set_xlabel("Training Steps", color="blue")
    ax.set_ylabel("Epsilon", color="blue")
    ax.tick_params(axis='x', colors="blue")
    ax.tick_params(axis='y', colors="blue")

    N = len(scores)
    running_avg = np.empty(N)
    for t in range(N):
        running_avg[t] = np.mean(scores[max(0, t-100):(t+1)])

    ax2.plot(x, running_avg, color="red")
    ax2.axes.get_xaxis().set_visible(False)
    ax2.yaxis.tick_right()
    ax2.set_ylabel('Score', color="red")
    ax2.yaxis.set_label_position('right')
    ax2.tick_params(axis='y', colors="red")

    plt.savefig(filename)