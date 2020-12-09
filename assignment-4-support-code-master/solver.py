from laser_tank import LaserTankMap, DotDict
import time
import random
import matplotlib.pyplot as plt

"""
Template file for you to implement your solution to Assignment 4. You should implement your solution by filling in the
following method stubs:
    train_q_learning()
    train_sarsa()
    get_policy()
    
You may add to the __init__ method if required, and can add additional helper methods and classes if you wish.

To ensure your code is handled correctly by the autograder, you should avoid using any try-except blocks in your
implementation of the above methods (as this can interfere with our time-out handling).

COMP3702 2020 Assignment 4 Support Code
"""


class Solver:
    def __init__(self, learning_rate=0.05):
        """
        Initialise solver to allow adjustable learning rate
        Used for graphing questions
        """
        self.learning_rate = learning_rate
        self.exploit_prob = 0.8
        self.averages = [] # Modelling ave of rewards
        self.rewards = [] # Modelling rewards
        self.iterations = [] # List to keep track of iteration numbers for plotting
        self.q_values = None

    @staticmethod
    def dict_argmax(state):
        """
        Return the maximum action for given state
        :param state: Dictionary containing action value pairs for a state
        :return: Action with largest value
        """
        return max(state, key=state.get)

    def get_iterations(self):
        """
        Returns list of iterations
        """
        return self.iterations

    def get_averages(self):
        """
        Returns list of averages
        """
        return self.averages

    def choose_action(self, state):
        """
        Selects an action based on epsilon-greedy strategy
        :return: Next action to take
        """
        state_dict = self.q_values.get(state)
        is_none = True

        for k in state_dict:
            if state_dict[k] != 0:
                is_none = False

        if random.random() > self.exploit_prob or is_none is True:
            action = random.choice(['f', 'l', 'r', 's'])
        else:
            action = Solver.dict_argmax(state_dict)

        return action

    def produce_average(self, t):
        sum = 0
        for i in range(50):
            sum += self.rewards[t - (50 + i)]
        return (sum / 50)


    def train_q_learning(self, simulator):
        """
        Train the agent using Q-learning, building up a table of Q-values.
        :param simulator: A simulator for collecting episode data (LaserTankMap instance)
        """
        # Q(s, a) table
        # suggested format: key = hash(state), value = dict(mapping actions to values)
        q_values = {}
        q_values[hash(simulator)] = {'f': 0, 'l': 0, 'r': 0, 's': 0}
        self.q_values = q_values
        current_state = simulator.make_clone()
        start_time = time.time()
        states = [current_state]
        step = 0

        while time.time() < start_time + simulator.time_limit: #i < 10000:
            cur_hash = hash(current_state)
            action = self.choose_action(cur_hash)
            next_state = current_state.make_clone()
            reward, is_finished = next_state.apply_move(action)

            # For graphing questions
            self.rewards.append(reward)
            if step > 50 and step < 12000:
                self.averages.append(self.produce_average(step))
                self.iterations.append(step - 50)

            # Fix for efficiency purposes
            if not is_finished and current_state not in states:
                states.append(current_state)

            q_s = self.q_values[cur_hash]
            old_q = q_s[action]
            next_hash = hash(next_state)

            if is_finished:
                best_next_q = 0
            else:
                next_s_q = {}
                for a in ['f', 'l', 'r', 's']:
                    next_s_q[a] = 0
                    if self.q_values.get(next_hash) is not None:
                        next_s_q[a] = self.q_values[next_hash][a]

                best_next_q = next_s_q[Solver.dict_argmax(next_s_q)]

            td = reward + (simulator.gamma * best_next_q) - old_q
            self.q_values[cur_hash][action] = old_q + (self.learning_rate * td)
            step += 1

            if is_finished:
                current_state = random.choice(states).make_clone()
            else:
                if self.q_values.get(next_hash) is None:
                    self.q_values[next_hash] = {'f': 0, 'l': 0, 'r': 0, 's': 0}
                current_state = next_state

    def train_sarsa(self, simulator):
        """
        Train the agent using SARSA, building up a table of Q-values.
        :param simulator: A simulator for collecting episode data (LaserTankMap instance)
        """

        # Q(s, a) table
        # suggested format: key = hash(state), value = dict(mapping actions to values)
        q_values = {}
        q_values[hash(simulator)] = {'f': 0, 'l': 0, 'r': 0, 's': 0}
        self.q_values = q_values
        current_state = simulator.make_clone()
        start_time = time.time()
        states = [current_state]
        cur_hash = hash(current_state)
        action = self.choose_action(cur_hash)
        step = 0

        while time.time() < start_time + simulator.time_limit:
            next_state = current_state.make_clone()
            reward, is_finished = next_state.apply_move(action)

            # For graphing questions
            self.rewards.append(reward)
            if step > 50 and step < 12000:
                self.averages.append(self.produce_average(step))
                self.iterations.append(step - 50)

            # Fix for efficiency purposes
            if not is_finished and current_state not in states:
                states.append(current_state)

            q_s = self.q_values[cur_hash]
            old_q = q_s[action]
            next_hash = hash(next_state)

            if is_finished:
                next_q = 0
                a = None
            else:
                if self.q_values.get(next_hash) is None:
                    self.q_values[next_hash] = {'f': 0, 'l': 0, 'r': 0, 's': 0}
                a = self.choose_action(next_hash)
                next_q = self.q_values[next_hash][a]

            td = reward + (simulator.gamma * next_q) - old_q
            self.q_values[cur_hash][action] = old_q + (self.learning_rate * td)
            step += 1

            if is_finished:
                current_state = random.choice(states).make_clone()
                cur_hash = hash(current_state)
                action = self.choose_action(cur_hash)
            else:
                current_state = next_state
                cur_hash = next_hash
                action = a

    def get_policy(self, state):
        """
        Get the policy for this state (i.e. the action that should be performed at this state).
        :param state: a LaserTankMap instance
        :return: pi(s) [an element of LaserTankMap.MOVES]
        """

        policy = self.q_values.get(hash(state))

        if policy is None:
            return None
        else:
            return Solver.dict_argmax(policy)







