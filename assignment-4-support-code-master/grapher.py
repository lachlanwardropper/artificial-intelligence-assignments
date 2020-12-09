import matplotlib.pyplot as plt
from laser_tank import LaserTankMap
from solver import Solver

def main(arglist):
    input_file = arglist[0]
    game_map = LaserTankMap.process_input_file(input_file)
    simulator = game_map.make_clone()

    # Question 3a
    solver1 = Solver(0.05)
    solver2 = Solver(0.0)
    solver3 = Solver(1)

    solver1.train_q_learning(simulator)
    iterations1 = solver1.get_iterations()
    averages1 = solver1.get_averages()
    print("Solver 1 Done")

    game_map = LaserTankMap.process_input_file(input_file)
    simulator = game_map.make_clone()
    solver2.train_q_learning(simulator)
    iterations2 = solver2.get_iterations()
    averages2 = solver2.get_averages()
    print("Solver 2 Done")

    game_map = LaserTankMap.process_input_file(input_file)
    simulator = game_map.make_clone()
    solver3.train_q_learning(simulator)
    iterations3 = solver3.get_iterations()
    averages3 = solver3.get_averages()
    print("Solver 3 Done")

    plt.plot(iterations1, averages1, 'r', iterations2, averages2, 'b', iterations3, averages3, 'g')
    plt.xlabel('Iterations')
    plt.ylabel('Average Moving Reward')
    plt.legend(['alpha = 0.05', 'alpha = 0.001', 'alpha = 0.95'])
    plt.title('Question 3a: Quality of Q-learning Policy Given Varied Alpha')
    plt.show()

    # Question 4a
    solver = Solver(0.05)
    game_map = LaserTankMap.process_input_file(arglist[1])
    simulator = game_map.make_clone()
    solver.train_sarsa(simulator)
    iterations = solver3.get_iterations()
    averages = solver3.get_averages()
    print("SARSA Solver Done")

    plt.plot(iterations1, averages1, 'r', iterations, averages, 'b')
    plt.xlabel('Iterations')
    plt.ylabel('Average Moving Reward')
    plt.legend(['q-learning', 'sarsa'])
    plt.title('Question 4a: Comparing Quality of Q-learning and SARSA')
    plt.show()

if __name__ == '__main__':
    main(['testcases/q-learn_t1.txt', 'testcases/sarsa_t1.txt'])