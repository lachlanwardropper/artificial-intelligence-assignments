from laser_tank import LaserTankMap, DotDict
import time
from copy import deepcopy

"""
Template file for you to implement your solution to Assignment 3. You should implement your solution by filling in the
following method stubs:
    run_value_iteration()
    run_policy_iteration()
    get_offline_value()
    get_offline_policy()
    get_mcts_policy()

You may add to the __init__ method if required, and can add additional helper methods and classes if you wish.

To ensure your code is handled correctly by the autograder, you should avoid using any try-except blocks in your
implementation of the above methods (as this can interfere with our time-out handling).

COMP3702 2020 Assignment 3 Support Code
"""


class Solver:

    def __init__(self, game_map):
        self.game_map = game_map

        #
        # TODO
        # Write any environment preprocessing code you need here (e.g. storing teleport locations).
        #
        # You may also add any instance variables (e.g. root node of MCTS tree) here.
        #
        # The allowed time for this method is 1 second, so your Value Iteration or Policy Iteration implementation
        # should be in the methods below, not here.
        #

        self.values = None
        self.policy = None
        self.transitions = []
        self.rewards = []

    def transition_function(self, state, action):
        """
        For each state-action pair, generate a set of possible next states and the probability
        associated with each one.
        :param state: Current state
        :param action: Action to take
        :return: Dict of next states -> probability associated
        """
        T = {}

        if state.player_heading == state.UP:
            # For action: Map next states + probability of getting them (1 for all but forward)
            if action == state.MOVE_FORWARD:
                # Successful forward
                next_y = state.player_y - 1
                next_x = state.player_x
                next_h = state.player_heading
                T[next_y, next_x, next_h] = state.t_success_prob

                # Up Left
                next_y = state.player_y - 1
                next_x = state.player_x - 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Up Right
                next_y = state.player_y - 1
                next_x = state.player_x + 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Left
                next_y = state.player_y
                next_x = state.player_x - 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Right
                next_y = state.player_y
                next_x = state.player_x + 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # No Change
                next_y = state.player_y
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5
            elif action == state.TURN_LEFT:
                T[state.player_y, state.player_x, state.LEFT] = 1
            elif action == state.TURN_RIGHT:
                T[state.player_y, state.player_x, state.RIGHT] = 1
            else:
                T[state.player_y, state.player_x, state.player_heading] = 1
        elif state.player_heading == state.RIGHT:
            if action == state.MOVE_FORWARD:
                # Successful forward
                next_y = state.player_y
                next_x = state.player_x + 1
                next_h = state.player_heading
                T[next_y, next_x, next_h] = state.t_success_prob

                # Up Left
                next_y = state.player_y - 1
                next_x = state.player_x + 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Up Right
                next_y = state.player_y + 1
                next_x = state.player_x + 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Left
                next_y = state.player_y - 1
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Right
                next_y = state.player_y + 1
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # No Change
                next_y = state.player_y
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5
            elif action == state.TURN_LEFT:
                T[state.player_y, state.player_x, state.UP] = 1
            elif action == state.TURN_RIGHT:
                T[state.player_y, state.player_x, state.DOWN] = 1
            else:
                T[state.player_y, state.player_x, state.player_heading] = 1
        elif state.player_heading == state.LEFT:
            if action == state.MOVE_FORWARD:
                # Successful forward
                next_y = state.player_y
                next_x = state.player_x - 1
                next_h = state.player_heading
                T[next_y, next_x, next_h] = state.t_success_prob

                # Up Left
                next_y = state.player_y + 1
                next_x = state.player_x - 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Up Right
                next_y = state.player_y - 1
                next_x = state.player_x - 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Left
                next_y = state.player_y + 1
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Right
                next_y = state.player_y - 1
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # No Change
                next_y = state.player_y
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5
            elif action == state.TURN_LEFT:
                T[state.player_y, state.player_x, state.DOWN] = 1
            elif action == state.TURN_RIGHT:
                T[state.player_y, state.player_x, state.UP] = 1
            else:
                T[state.player_y, state.player_x, state.player_heading] = 1
        else:
            if action == state.MOVE_FORWARD:
                # Successful forward
                next_y = state.player_y + 1
                next_x = state.player_x
                next_h = state.player_heading
                T[next_y, next_x, next_h] = state.t_success_prob

                # Up Left
                next_y = state.player_y + 1
                next_x = state.player_x + 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Up Right
                next_y = state.player_y + 1
                next_x = state.player_x - 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Left
                next_y = state.player_y
                next_x = state.player_x + 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # Right
                next_y = state.player_y
                next_x = state.player_x - 1
                T[next_y, next_x, next_h] = state.t_error_prob / 5

                # No Change
                next_y = state.player_y
                next_x = state.player_x
                T[next_y, next_x, next_h] = state.t_error_prob / 5
            elif action == state.TURN_LEFT:
                T[state.player_y, state.player_x, state.RIGHT] = 1
            elif action == state.TURN_RIGHT:
                T[state.player_y, state.player_x, state.LEFT] = 1
            else:
                T[state.player_y, state.player_x, state.player_heading] = 1

        if action == state.MOVE_FORWARD:
            newT = {}
            ind = 0
            for t in T:
                next_y = t[0]
                next_x = t[1]
                next_h = t[2]
                prob = T[t]

                if next_y >= state.y_size or next_x >= state.x_size or next_y < 0 or next_x < 0:
                    newT[next_y, next_x, next_h, ind] = prob
                else:
                    # handle special tile types
                    if state.grid_data[next_y][next_x] == state.ICE_SYMBOL:
                        # handle ice tile - slide until first non-ice tile or blocked
                        if next_h == state.UP:
                            for i in range(next_y, -1, -1):
                                if state.grid_data[i][next_x] != state.ICE_SYMBOL:
                                    if state.grid_data[i][next_x] == state.WATER_SYMBOL:
                                        # slide into water - game over
                                        next_y = i
                                        break
                                    elif state.cell_is_blocked(i, next_x):
                                        # if blocked, stop on last ice cell
                                        next_y = i + 1
                                        break
                                    else:
                                        next_y = i
                                        break
                        elif next_h == state.DOWN:
                            for i in range(next_y, state.y_size):
                                if state.grid_data[i][next_x] != state.ICE_SYMBOL:
                                    if state.grid_data[i][next_x] == state.WATER_SYMBOL:
                                        # slide into water - game over
                                        next_y = i
                                        break
                                    elif state.cell_is_blocked(i, next_x):
                                        # if blocked, stop on last ice cell
                                        next_y = i - 1
                                        break
                                    else:
                                        next_y = i
                                        break
                        elif next_h == state.LEFT:
                            for i in range(next_x, -1, -1):
                                if state.grid_data[next_y][i] != state.ICE_SYMBOL:
                                    if state.grid_data[next_y][i] == state.WATER_SYMBOL:
                                        # slide into water - game over
                                        next_x = i
                                        break
                                    elif state.cell_is_blocked(next_y, i):
                                        # if blocked, stop on last ice cell
                                        next_x = i + 1
                                        break
                                    else:
                                        next_x = i
                                        break
                        else:
                            for i in range(next_x, state.x_size):
                                if state.grid_data[next_y][i] != state.ICE_SYMBOL:
                                    if state.grid_data[next_y][i] == state.WATER_SYMBOL:
                                        # slide into water - game over
                                        next_x = i
                                        break
                                    elif state.cell_is_blocked(next_y, i):
                                        # if blocked, stop on last ice cell
                                        next_x = i - 1
                                        break
                                    else:
                                        next_x = i
                                        break
                    if state.grid_data[next_y][next_x] == state.TELEPORT_SYMBOL:
                        # handle teleport - find the other teleporter
                        tpy, tpx = (None, None)
                        for i in range(state.y_size):
                            for j in range(state.x_size):
                                if state.grid_data[i][j] == state.TELEPORT_SYMBOL and i != next_y and j != next_x:
                                    tpy, tpx = (i, j)
                                    break
                            if tpy is not None:
                                break
                        if tpy is None:
                            raise Exception("LaserTank Map Error: Unmatched teleport symbol")
                        next_y, next_x = (tpy, tpx)
                        newT[next_y, next_x, next_h, ind] = prob
                    else:
                        newT[next_y, next_x, next_h, ind] = prob
                ind += 1
            return newT
        else:
            return T

    def get_offline_value(self, state):
        """
        Get the value of this state.
        :param state: a LaserTankMap instance
        :return: V(s) [a floating point number]
        """
        x_or = state.player_x
        y_or = state.player_y
        h_or = state.player_heading
        i = 0
        totals = {}

        # Sum transition function * (reward + next value function) - don't use apply move
        for action in state.MOVES:
            r = 0
            TV = 0
            state.player_heading = h_or
            T = self.transitions[y_or][x_or][h_or][i]
            j = 0
            for t in T:
                # get reward value (look at apply_move) and get eps (using values array)
                y_pos = t[0]
                x_pos = t[1]
                heading = t[2]
                prob = T[t]

                rew = self.rewards[y_or][x_or][h_or][i][j]

                if y_pos >= state.y_size or x_pos >= state.x_size or y_pos < 0 or x_pos < 0:
                    y_pos = state.player_y
                    x_pos = state.player_x
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]
                elif rew == state.collision_cost:
                    y_pos = state.player_y
                    x_pos = state.player_x
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]
                elif rew == state.game_over_cost:
                    y_pos = state.player_y
                    x_pos = state.player_x
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]
                else:
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]

                TV += prob * s_prime

                j += 1

            total = r + state.gamma * TV
            totals[action] = total
            i += 1

        return max(totals.values()), max(totals, key=totals.get)

    def run_value_iteration(self):
        """
        Build a value table and a policy table using value iteration, and store inside self.values and self.policy.
        """
        values = [[[0 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]
        policy = [[[-1 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]

        self.transitions = [[[[{}, {}, {}, {}] for a in range(4)]
                             for x in range(0, self.game_map.x_size)] for y in range(0, self.game_map.y_size)]

        self.rewards = [[[[[] for a in range(4)] for d in range(4)]
                             for x in range(0, self.game_map.x_size)] for y in range(0, self.game_map.y_size)]

        self.values = values
        self.policy = policy

        original_x = self.game_map.player_x
        original_y = self.game_map.player_y
        original_h = self.game_map.player_heading

        deltas = [10]

        time_lim = time.time() + self.game_map.time_limit
        state = self.game_map
        for y in range(self.game_map.y_size):
            for x in range(self.game_map.x_size):
                for d in range(4):
                    i = 0
                    for a in ['f', 'l', 'r', 's']:
                        state.player_y = y
                        state.player_x = x
                        state.player_heading = d
                        self.transitions[y][x][d][i] = self.transition_function(state, a)
                        T = self.transitions[y][x][d][i]

                        rewards = []

                        for t in T:
                            y_pos = t[0]
                            x_pos = t[1]

                            if y_pos >= state.y_size or x_pos >= state.x_size or y_pos < 0 or x_pos < 0:
                                reward = state.collision_cost
                            elif state.cell_is_game_over(y_pos, x_pos):
                                reward = state.game_over_cost
                            elif state.cell_is_blocked(y_pos, x_pos):
                                reward = state.collision_cost
                            else:
                                reward = state.move_cost

                            rewards.append(reward)
                        self.rewards[y][x][d][i] = rewards
                        i += 1

        while time.time() < time_lim:
            deltas_abs = [abs(ele) for ele in deltas]
            if max(deltas_abs) < self.game_map.epsilon:
                break
            else:
                deltas.clear()
                for y in range(self.game_map.y_size):
                    for x in range(self.game_map.x_size):
                        for d in range(4):
                            state.player_y = y
                            state.player_x = x
                            state.player_heading = d

                            if state.cell_is_blocked(y, x):
                                V = 0
                                P = -1
                            elif state.cell_is_game_over(y, x):
                                V = state.game_over_cost
                                P = -1
                            elif state.is_finished():
                                V = state.goal_reward
                                P = -1
                            else:
                                old_val = values[x][y][d]
                                V, P = self.get_offline_value(state)
                                deltas.append(V - old_val)

                            values[x][y][d] = V
                            policy[x][y][d] = P

                self.values = values
                self.policy = policy

        self.game_map.player_x = original_x
        self.game_map.player_y = original_y
        self.game_map.player_heading = original_h

    def policy_improvement(self, state):
        """
        Extract the best policy for a given value function
        :param state: State to check
        :return: Best policy
        """
        x_or = state.player_x
        y_or = state.player_y
        h_or = state.player_heading
        i = 0
        totals = {}

        for action in state.MOVES:
            TV = 0
            r = 0
            state.player_x = x_or
            state.player_y = y_or
            state.player_heading = h_or
            T = self.transitions[y_or][x_or][h_or][i]
            j = 0
            for t in T:
                # get reward value (look at apply_move) and get eps (using values array)
                y_pos = t[0]
                x_pos = t[1]
                heading = t[2]
                prob = T[t]

                rew = self.rewards[y_or][x_or][h_or][i][j]

                if y_pos >= state.y_size or x_pos >= state.x_size or y_pos < 0 or x_pos < 0:
                    y_pos = state.player_y
                    x_pos = state.player_x
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]
                elif rew == state.collision_cost:
                    y_pos = state.player_y
                    x_pos = state.player_x
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]
                elif rew == state.game_over_cost:
                    y_pos = state.player_y
                    x_pos = state.player_x
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]
                else:
                    r += rew * prob
                    s_prime = self.values[x_pos][y_pos][heading]

                TV += prob * s_prime

                j += 1

            total = r + state.gamma * TV
            totals[action] = total
            i += 1

        return max(totals, key=totals.get)

    def get_offline_policy(self, state):
        """
        Get the policy for this state (i.e. the action that should be performed at this state).
        :param state: a LaserTankMap instance
        :return: pi(s) [an element of LaserTankMap.MOVES]
        """

        return self.policy[state.player_x][state.player_y][state.player_heading]

    def next_evaluation_iteration(self, state):
        """
        Evaluate next iteration in policy iteration
        :param state: State to test
        """
        x_or = state.player_x
        y_or = state.player_y
        h_or = state.player_heading
        r = 0
        a = self.policy[x_or][y_or][h_or]

        # Check what action is selected
        if a == 'f':
            i = 0
        elif a == 'l':
            i = 1
        elif a == 'r':
            i = 2
        else:
            i = 3

        T = self.transitions[y_or][x_or][h_or][i]
        state.player_x = x_or
        state.player_y = y_or
        state.player_heading = h_or
        TV = 0
        j = 0
        for t in T:
            # get reward value (look at apply_move) and get eps (using values array)
            y_pos = t[0]
            x_pos = t[1]
            heading = t[2]
            prob = T[t]

            rew = self.rewards[y_or][x_or][h_or][i][j]

            if y_pos >= state.y_size or x_pos >= state.x_size or y_pos < 0 or x_pos < 0:
                y_pos = state.player_y
                x_pos = state.player_x
                r += rew * prob
                s_prime = self.values[x_pos][y_pos][heading]
            elif rew == state.collision_cost:
                y_pos = state.player_y
                x_pos = state.player_x
                r += rew * prob
                s_prime = self.values[x_pos][y_pos][heading]
            elif rew == state.game_over_cost:
                y_pos = state.player_y
                x_pos = state.player_x
                r += rew * prob
                s_prime = self.values[x_pos][y_pos][heading]
            else:
                r += rew * prob
                s_prime = self.values[x_pos][y_pos][heading]

            TV += prob * s_prime

            j += 1

        total = r + state.gamma * TV
        return total

    def run_policy_iteration(self):
        """
        Build a value table and a policy table using policy iteration, and store inside self.values and self.policy.
        """
        values = [[[0 for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]
        policy = [[['f' for _ in LaserTankMap.DIRECTIONS]
                   for __ in range(0, self.game_map.y_size)]
                  for ___ in range(0, self.game_map.x_size)]

        time_init = time.time()

        # store the computed values and policy
        self.values = values
        self.policy = policy
        deltas = [10]
        original_x = self.game_map.player_x
        original_y = self.game_map.player_y
        original_h = self.game_map.player_heading

        self.transitions = [[[[{}, {}, {}, {}] for a in range(4)]
                             for x in range(0, self.game_map.x_size)] for y in range(0, self.game_map.y_size)]

        self.rewards = [[[[[] for a in range(4)] for d in range(4)]
                         for x in range(0, self.game_map.x_size)] for y in range(0, self.game_map.y_size)]

        state = self.game_map
        for y in range(self.game_map.y_size):
            for x in range(self.game_map.x_size):
                for d in range(4):
                    i = 0
                    for a in ['f', 'l', 'r', 's']:
                        state.player_y = y
                        state.player_x = x
                        state.player_heading = d
                        self.transitions[y][x][d][i] = self.transition_function(state, a)
                        T = self.transitions[y][x][d][i]

                        rewards = []

                        for t in T:
                            y_pos = t[0]
                            x_pos = t[1]

                            if y_pos >= state.y_size or x_pos >= state.x_size or y_pos < 0 or x_pos < 0:
                                reward = state.collision_cost
                            elif state.cell_is_game_over(y_pos, x_pos):
                                reward = state.game_over_cost
                            elif state.cell_is_blocked(y_pos, x_pos):
                                reward = state.collision_cost
                            else:
                                reward = state.move_cost

                            rewards.append(reward)
                        self.rewards[y][x][d][i] = rewards
                        i += 1

        time_lim = time.time() + self.game_map.time_limit

        while time.time() < time_lim:
            deltas_abs = [abs(ele) for ele in deltas]
            if max(deltas_abs) < self.game_map.epsilon:

                break
            else:
                deltas.clear()
                for y in range(10):
                    for y in range(self.game_map.y_size):
                        for x in range(self.game_map.x_size):
                            for d in range(4):
                                old_val = values[x][y][d]

                                state.player_y = y
                                state.player_x = x
                                state.player_heading = d

                                if state.cell_is_blocked(y, x):
                                    V = 0
                                elif state.cell_is_game_over(y, x):
                                    V = state.game_over_cost
                                elif state.is_finished():
                                    V = state.goal_reward
                                else:
                                    V = self.next_evaluation_iteration(state)

                                values[x][y][d] = V
                                deltas.append(V - old_val)

                    self.values = values

                for y in range(self.game_map.y_size):
                    for x in range(self.game_map.x_size):
                        for d in range(4):

                            state.player_y = y
                            state.player_x = x
                            state.player_heading = d

                            if state.cell_is_blocked(y, x) or state.cell_is_game_over(y, x) or state.is_finished():
                                P = -1
                            else:
                                P = self.policy_improvement(state)

                            policy[x][y][d] = P

                self.policy = policy

        self.game_map.player_x = original_x
        self.game_map.player_y = original_y
        self.game_map.player_heading = original_h
        self.values = values
        self.policy = policy


    def get_mcts_policy(self, state):
        """
        Choose an action to be performed using online MCTS.
        :param state: a LaserTankMap instance
        :return: pi(s) [an element of LaserTankMap.MOVES]
        """

        #
        # TODO
        # Write your Monte-Carlo Tree Search implementation here.
        #
        # Each time this method is called, you are allowed up to [state.time_limit] seconds of compute time - make sure
        # you stop searching before this time limit is reached.
        #

        pass






